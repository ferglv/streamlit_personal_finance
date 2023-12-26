# backend/xml_processing/xml_parser.py
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional, Tuple
from xml.etree.ElementTree import Element

from streamlit.runtime.uploaded_file_manager import UploadedFile


def get_namespace(root: Element) -> Optional[str]:
    """
    Extracts the CFDI namespace from the XML root element.

    Args:
        root (Element): The root element of the XML document.

    Returns:
        Optional[str]: The extracted namespace string or None if not found.
    """
    if "}" in root.tag:
        return root.tag.split("}")[0].strip("{").split("/")[-1]
    return None


def extract_emisor_nomina_info(
    root: Element, namespaces: Dict[str, str]
) -> Tuple[str, Optional[Element]]:
    """
    Extracts common information from 'Emisor' and 'Nomina' nodes in the XML document.

    Args:
        root (Element): The root element of the XML document.
        namespaces (Dict[str, str]): The namespaces for XML parsing.

    Returns:
        Tuple[str, Optional[Element]]: A tuple containing the name of the 'Emisor' and the 'Nomina' element.
    """
    emisor = root.find("cfdi:Emisor", namespaces)
    emisor_name = (
        emisor.get("Nombre", "Not Found") if emisor is not None else "Not Found"
    )
    nomina = root.find(".//nomina12:Nomina", namespaces)
    return emisor_name, nomina


def parse_deductions(
    nomina: Optional[Element], namespaces: Dict[str, str]
) -> Tuple[str, str]:
    """
    Parses deduction information from the 'Nomina' node.

    Args:
        nomina (Optional[Element]): The 'Nomina' element from the XML document.
        namespaces (Dict[str, str]): The namespaces for XML parsing.

    Returns:
        Tuple[str, str]: The extracted IMSS and ISR deduction amounts.
    """
    if nomina is None:
        return "0.00", "0.00"

    deducciones = nomina.find("nomina12:Deducciones", namespaces)
    imss = isr = "0.00"
    if deducciones:
        for deduccion in deducciones.findall("nomina12:Deduccion", namespaces):
            tipo_deduccion = deduccion.get("TipoDeduccion")
            importe = deduccion.get("Importe", "0.00")
            if tipo_deduccion == "001":
                imss = importe
                if isr != "0.00":
                    break
            elif tipo_deduccion == "002":
                isr = importe
                if imss != "0.00":
                    break
    return imss, isr


def parse_xml(file_path: UploadedFile) -> Optional[dict]:
    """
    Parses an individual XML file to extract payroll information and format it into an SQL insert statement.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        Optional[dict]: data dict with xml information or None in case of failure.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        cfdi_version = get_namespace(root)
        if not cfdi_version:
            raise ValueError("CFDI namespace not found in XML")

        namespaces = {
            "cfdi": f"http://www.sat.gob.mx/cfd/{cfdi_version}",
            "nomina12": "http://www.sat.gob.mx/nomina12",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
        }

        emisor_name, nomina = extract_emisor_nomina_info(root, namespaces)
        position = (
            nomina.find("nomina12:Receptor", namespaces).get("Puesto", "Not Found")
            if nomina
            else "Not Found"
        )
        fecha_inicial_pago = (
            nomina.get("FechaInicialPago", "Not Found") if nomina else "Not Found"
        )
        fecha_final_pago = (
            nomina.get("FechaFinalPago", "Not Found") if nomina else "Not Found"
        )
        subtotal = root.get("SubTotal", "0.00")

        imss, isr = parse_deductions(nomina, namespaces)
        uuid = root.find(".//tfd:TimbreFiscalDigital", namespaces).get("UUID")

        fecha_inicial_pago = datetime.strptime(fecha_inicial_pago, "%Y-%m-%d").date()
        fecha_final_pago = datetime.strptime(fecha_final_pago, "%Y-%m-%d").date()

        data = {
            "start_date": fecha_inicial_pago,
            "end_date": fecha_final_pago,
            "fiscal_folio": uuid,
            "client": emisor_name,
            "position": position,
            "gross_income": subtotal,
            "imss": imss,
            "isr": isr,
        }

        return data
    except ET.ParseError as e:
        print(f"XML parsing error in file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing file {file_path}: {e}")
        return None

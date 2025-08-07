from typing import Any, Text, Dict, List
import json
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


def load_certificate_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, 'certificate_data.json')

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Create both versions (with space and underscore)
            normalized_data = {}
            for key, value in data.items():
                normalized_data[key] = value
                normalized_data[key.replace('_', ' ')] = value
            return normalized_data
    except Exception as e:
        print(f"Error loading certificate data: {str(e)}")
        return {}
CERT_DATA = load_certificate_data()
class ActionResetCertificateType(Action):
    def name(self) -> Text:
        return "action_reset_certificate_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("certificate_type", None)]
class ActionProvideCertificateInfo(Action):
    def name(self) -> Text:
        return "action_provide_certificate_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="Please specify which certificate you need information about.")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have information about {cert_type} certificates.")
            return []

        # Handle different certificate structures
        if 'definition' in cert_info:  # Standard certificates
            description = cert_info['definition']
        elif 'purpose' in cert_info:  # Some special certificates might use 'purpose'
            description = cert_info['purpose']
        else:
            description = "No description available"

        issuing_auth = cert_info.get('issuing_authority', 'Not specified')

        # Create formatted response
        response = [
            f"📌 *{cert_info.get('name', cert_type.title())}*",
            "",
            "📝 Description:",
            f"{description}\n",
            "",
            "🏛️ Issuing Authority:",
            f"{issuing_auth}\n"
        ]

        # Special handling for passport types
        if cert_type.lower() in ['passport', 'passports'] and 'types_of_passport' in cert_info:
            response.extend([
                "",
                "📋 Types Available:\n"
            ])
            for p_type, p_desc in cert_info['types_of_passport'].items():
                response.append(f"• {p_type.replace('_', ' ').title()}: {p_desc}\n")

        # Join all parts with newlines
        formatted_response = "\n".join(response)
        dispatcher.utter_message(text=formatted_response)
        return []

class ActionProvideApplicationProcess(Action):
    def name(self) -> Text:
        return "action_provide_application_process"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like the application process?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have application process details for {cert_type}.")
            return []

        # Handle different process structures
        process_info = None
        if 'application_process' in cert_info:
            if isinstance(cert_info['application_process'], list):
                process_info = {'steps': cert_info['application_process']}
            else:
                process_info = cert_info['application_process']
        elif 'learner_license' in cert_info:  # Driving license special case
            process_info = cert_info['learner_license']

        if not process_info or 'steps' not in process_info:
            dispatcher.utter_message(text=f"Sorry, application process not available for {cert_type}.")
            return []

        # Create formatted response
        response = [
            f"📋 Application Process for {cert_info.get('name', cert_type.title())}",
            ""
        ]

        # Add steps
        response.append("🔹 Steps:")
        for i, step in enumerate(process_info['steps'], 1):
            response.append(f"{i}. {step}\n")

        # Add processing time if available
        if 'processing_time' in process_info:
            response.extend([
                "",
                "⏱️ Processing Time:"
            ])
            if isinstance(process_info['processing_time'], dict):
                for time_type, duration in process_info['processing_time'].items():
                    response.append(f"• {time_type.title()}: {duration}")
            else:
                response.append(f"{process_info['processing_time']}")

        # Add where to apply if available
        if 'where_to_apply' in process_info:
            response.extend([
                "",
                "📍 Where to Apply:",
                f"{process_info['where_to_apply']}"
            ])

        formatted_response = "\n".join(response)
        dispatcher.utter_message(text=formatted_response)
        return []

class ActionProvideDocumentsList(Action):
    def name(self) -> Text:
        return "action_provide_documents_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like the required documents?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have document requirements for {cert_type}.")
            return []

        # Get documents list
        docs = cert_info.get('documents_needed', [])
        if not docs:
            dispatcher.utter_message(text=f"Sorry, document requirements not available for {cert_type}.")
            return []

        # Build the response
        response = f"Documents Required for {cert_type.title()}:"

        # Add bullet points for each document
        for doc in docs:
            response += f"• {doc}\n"


        # Send the complete message
        dispatcher.utter_message(text=response)
        return []

class ActionProvideCostInfo(Action):
    def name(self) -> Text:
        return "action_provide_cost_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like fee information?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have fee details for {cert_type}.")
            return []

        # Handle different fee structures
        fees = {}
        if 'cost' in cert_info:
            fees = cert_info['cost']
        elif 'fee_structure' in cert_info:
            fees = cert_info['fee_structure']
        elif 'fees' in cert_info:
            fees = cert_info['fees']

        # Special handling for passport tatkal fees
        if cert_type.lower() in ['passport', 'passports'] and 'tatkal_passport_procedure' in cert_info:
            tatkal_fees = cert_info['tatkal_passport_procedure'].get('processing_fee')
            if tatkal_fees:
                fees['tatkal'] = tatkal_fees

        if not fees:
            dispatcher.utter_message(text=f"Fee information not available for {cert_type}.")
            return []

        # Create formatted response
        response = [
            f"💰 Fees for {cert_info.get('name', cert_type.title())}",
            ""
        ]

        if isinstance(fees, dict):
            for fee_type, amount in fees.items():
                if isinstance(amount, dict):  # Nested fee structure
                    response.append(f"💳 {fee_type.replace('_', ' ').title()}:")
                    for sub_type, sub_amount in amount.items():
                        response.append(f"  • {sub_type.replace('_', ' ').title()}: {sub_amount}")
                else:
                    response.append(f"• {fee_type.replace('_', ' ').title()}: {amount}")
        else:
            response.append(f"• Standard Fee*: {fees}")

        formatted_response = "\n".join(response)
        dispatcher.utter_message(text=formatted_response)
        return []

class ActionProvidePassportTatkalInfo(Action):
    def name(self) -> Text:
        return "action_provide_passport_tatkal_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cert_info = CERT_DATA.get('passport') or CERT_DATA.get('passports')
        if not cert_info or 'tatkal_passport_procedure' not in cert_info:
            dispatcher.utter_message(text="Sorry, I don't have Tatkal passport information available.")
            return []

        tatkal = cert_info['tatkal_passport_procedure']

        response = [
            "🚨 *Tatkal Passport Procedure*",
            "",
            f"✅ *Eligibility:* {tatkal.get('eligibility', 'Not specified')}",
            "",
            "📄 *Additional Documents Needed:*"
        ]

        response.extend([f"• {doc}" for doc in tatkal.get('additional_documents_needed', [])])
        response.extend([
            "",
            f"💰 *Processing Fee:* {tatkal.get('processing_fee', 'Not specified')}",
            f"⏱️ *Processing Time:* {tatkal.get('processing_time', 'Not specified')}"
        ])

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideLicenseTypes(Action):
    def name(self) -> Text:
        return "action_provide_license_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_info = CERT_DATA.get('driving license') or CERT_DATA.get('driving_license')
        if not cert_info or 'types_of_license' not in cert_info:
            dispatcher.utter_message(text="Sorry, I don't have driving license type information available.")
            return []

        response = [
            "🚗 Types of Driving Licenses",
            ""
        ]

        for l_type, l_desc in cert_info['types_of_license'].items():
            response.append(f"• {l_type.replace('_', ' ').title()}: {l_desc}")

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideDuplicateInfo(Action):
    def name(self) -> Text:
        return "action_provide_duplicate_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate do you need duplicate information?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have duplicate certificate details for {cert_type}.")
            return []

        # Handle different structures
        dup_info = None
        if 'duplicate_certificate' in cert_info:
            dup_info = cert_info['duplicate_certificate']
        elif 'lost_or_damaged_passport' in cert_info:
            dup_info = cert_info['lost_or_damaged_passport']

        if not dup_info:
            dispatcher.utter_message(text=f"Duplicate process not available for {cert_type}.")
            return []

        response = [
            f"🔄 Process for Duplicate {cert_info.get('name', cert_type.title())}",
            ""
        ]

        if 'how_to_get' in dup_info:
            response.append("📝 Steps to Obtain Duplicate:")
            response.extend([f"{i + 1}. {step}" for i, step in enumerate(dup_info['how_to_get'])])
        elif 'how_to_replace' in dup_info:
            response.append("📝 Replacement Process:")
            response.extend([f"{i + 1}. {step}" for i, step in enumerate(dup_info['how_to_replace'])])

        if 'processing_time' in dup_info:
            response.extend([
                "",
                f"⏱️ Processing Time:* {dup_info['processing_time']}"
            ])
        if 'cost' in dup_info:
            response.extend([
                "",
                f"💰 Cost:* ₹{dup_info['cost']}"
            ])

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideIssuingAuthority(Action):
    def name(self) -> Text:
        return "action_provide_issuing_authority"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="Please specify which certificate's issuing authority you need.")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have issuing authority information for {cert_type}.")
            return []

        issuing_auth = cert_info.get('issuing_authority') or cert_info.get('issued_by') or cert_info.get(
            'issuing_office')
        if not issuing_auth:
            dispatcher.utter_message(text=f"Issuing authority information not available for {cert_type}.")
            return []

        response = [
            f"🏛️ Issuing Authority for {cert_info.get('name', cert_type.title())}",
            "",
            issuing_auth
        ]

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionCheckEligibility(Action):
    def name(self) -> Text:
        return "action_check_eligibility"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like to check eligibility?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info or 'eligibility' not in cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have eligibility criteria for {cert_type}.")
            return []

        eligibility = cert_info['eligibility']
        response = [
            f"✅ Eligibility for {cert_info.get('name', cert_type.title())}",
            ""
        ]

        if cert_type.lower() in ['driving license', 'driving_license']:
            response.append("🛵 *Learner's License:*")
            if 'age_requirement' in eligibility.get('learner_license', {}):
                for vehicle, requirement in eligibility['learner_license']['age_requirement'].items():
                    response.append(f"• *{vehicle.replace('_', ' ').title()}*: {requirement}")
            if 'other_requirements' in eligibility.get('learner_license', {}):
                response.extend([
                    "",
                    "📌 Other Requirements:",
                    eligibility['learner_license']['other_requirements']
                ])

            response.extend([
                "",
                "🚘 Permanent License:"
            ])
            if 'requirements' in eligibility.get('permanent_license', {}):
                response.append(eligibility['permanent_license']['requirements'])
        else:
            if isinstance(eligibility, dict):
                for key, value in eligibility.items():
                    if isinstance(value, dict):
                        response.append(f"📌 {key.replace('_', ' ').title()}:")
                        for sub_key, sub_value in value.items():
                            response.append(f"  • {sub_key.replace('_', ' ').title()}: {sub_value}")
                    else:
                        response.append(f"• {key.replace('_', ' ').title()}: {value}")
            else:
                response.append(str(eligibility))

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvidePassportTypes(Action):
    def name(self) -> Text:
        return "action_provide_passport_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_info = CERT_DATA.get('passport') or CERT_DATA.get('passports')
        if not cert_info or 'types_of_passport' not in cert_info:
            dispatcher.utter_message(text="Sorry, I don't have passport type information available.")
            return []

        response = [
            "🛂 Types of Passports",
            ""
        ]

        for p_type, p_desc in cert_info['types_of_passport'].items():
            response.append(f"• {p_type.replace('_', ' ').title()}: {p_desc}")

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideOnlineApplicationInfo(Action):
    def name(self) -> Text:
        return "action_provide_online_application_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like online application information?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        online_portal = None

        if 'online_portal' in cert_info:
            online_portal = cert_info['online_portal']
        elif 'application_process' in cert_info and 'where_to_apply' in cert_info['application_process']:
            if 'http' in cert_info['application_process']['where_to_apply']:
                online_portal = cert_info['application_process']['where_to_apply']
        elif 'online_services' in cert_info and 'apply_online' in cert_info['online_services']:
            online_portal = cert_info['online_services']['apply_online']

        if not online_portal:
            dispatcher.utter_message(text=f"Sorry, online application is not available for {cert_type}.")
            return []

        response = [
            f"🌐 Online Application for {cert_info.get('name', cert_type.title())}",
            "",
            f"🔗 Portal: {online_portal}",
            "",
            "📋 Application Steps:",
            "1. Visit the portal",
            "2. Create an account",
            "3. Fill the application form",
            "4. Upload required documents",
            "5. Pay the fees",
            "6. Track your application"
        ]

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideProcessingTime(Action):
    def name(self) -> Text:
        return "action_provide_processing_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like processing time information?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have processing time details for {cert_type}.")
            return []

        processing_info = None

        if 'processing_time' in cert_info:
            processing_info = cert_info['processing_time']
        elif 'application_process' in cert_info and isinstance(cert_info['application_process'], dict):
            processing_info = cert_info['application_process'].get('processing_time')
        elif cert_type.lower() in ['passport', 'passports'] and 'tatkal_passport_procedure' in cert_info:
            processing_info = {
                'normal': cert_info.get('processing_time', 'Not specified'),
                'tatkal': cert_info['tatkal_passport_procedure'].get('processing_time', '1-3 days')
            }

        if not processing_info:
            dispatcher.utter_message(text=f"Processing time information not available for {cert_type}.")
            return []

        response = [
            f"⏱️ Processing Time for {cert_info.get('name', cert_type.title())}",
            ""
        ]

        if isinstance(processing_info, dict):
            for time_type, duration in processing_info.items():
                response.append(f"• {time_type.replace('_', ' ').title()}: {duration}")
        elif isinstance(processing_info, list):
            response.extend([f"• {item}" for item in processing_info])
        else:
            response.append(f"• Standard Processing: {processing_info}")

        # Additional time-related information
        if 'duplicate_card' in cert_info and 'processing_time' in cert_info['duplicate_card']:
            response.extend([
                "",
                f"• Duplicate Processing: {cert_info['duplicate_card']['processing_time']}"
            ])
        if 'correction_or_update' in cert_info and 'processing_time' in cert_info['correction_or_update']:
            response.extend([
                "",
                f"• Correction Processing: {cert_info['correction_or_update']['processing_time']}"
            ])

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideRationCardTypes(Action):
    def name(self) -> Text:
        return "action_provide_ration_card_types"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_info = CERT_DATA.get('ration card') or CERT_DATA.get('ration_card')
        if not cert_info or 'types_of_ration_cards' not in cert_info:
            dispatcher.utter_message(text="Sorry, ration card type information isn't available.")
            return []

        response = [
            "🛒 Types of Ration Cards",
            "",
            "The Public Distribution System issues these card types:",
            ""
        ]

        for card_type, description in cert_info['types_of_ration_cards'].items():
            response.append(f"• {card_type.upper()}: {description}")
            response.append("\n")

        dispatcher.utter_message(text="\n".join(response))
        return []

class ActionProvideValidityInfo(Action):
    def name(self) -> Text:
        return "action_provide_validity_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        cert_type = tracker.get_slot("certificate_type")
        if not cert_type:
            dispatcher.utter_message(text="For which certificate would you like validity information?")
            return []

        cert_info = CERT_DATA.get(cert_type.lower()) or CERT_DATA.get(cert_type.lower().replace(' ', '_'))
        if not cert_info:
            dispatcher.utter_message(text=f"Sorry, I don't have validity information for {cert_type}.")
            return []

        validity = cert_info.get('validity') or cert_info.get('expiry') or "Typically valid until cancelled or updated"

        response = [
            f"📅 Validity Information for {cert_info.get('name', cert_type.title())}",
            "",
            validity
        ]

        dispatcher.utter_message(text="\n".join(response))
        return []
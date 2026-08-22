        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=user_message,
            config={
                "system_instruction": "Eres Bexia, una entidad digital autonoma creada por Fer."
            }
        )

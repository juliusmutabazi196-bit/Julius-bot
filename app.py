        # --- ADMIN mutabazi196 COMMANDS ---
        if text.startswith(ADMIN_CODE):
            cmd = text.replace(ADMIN_CODE, "").strip()

            # 1. BROADCAST to all
            if cmd.startswith("broadcast:"):
                b_msg = cmd.split("broadcast:")[1].strip()
                for num in broadcast_list:
                    send_whatsapp(num, b_msg)
                send_whatsapp(from_num, f"Broadcast sent to {len(broadcast_list)} ✅")
                return "ok", 200

            # 2. GRANT FREE ACCESS
            # Usage: mutabazi196 free 0781234567 30
            if cmd.startswith("free"):
                parts = cmd.split()
                free_phone = parts[1] # 078...
                days = int(parts[2]) if len(parts) > 2 else 30
                wa_phone = free_phone.replace("0","256",1) if free_phone.startswith("0") else free_phone
                paid_users[wa_phone] = datetime.now() + timedelta(days=days)
                send_whatsapp(from_num, f"FREE granted to {free_phone} for {days} days ✅")
                send_whatsapp(wa_phone, f"Webale! Wagabiirwe FREE access ya AI ya Runyankore Rukiiga for {days} days! Obu orikushobora kubuuza byona.")
                return "ok", 200

            # 3. CHAT AS YOU PERSONALLY
            # Usage: mutabazi196 chat 0781234567 Agandiire, ndi Julius nyine!
            if cmd.startswith("chat"):
                parts = cmd.split(" ", 2)
                target = parts[1]
                personal_msg = parts[2] if len(parts) > 2 else ""
                wa_target = target.replace("0","256",1) if target.startswith("0") else target
                send_whatsapp(wa_target, personal_msg)
                send_whatsapp(from_num, f"Sent as you to {target}: {personal_msg} ✅")
                return "ok", 200

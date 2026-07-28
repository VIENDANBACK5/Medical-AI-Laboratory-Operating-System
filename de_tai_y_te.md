# 🏥 Danh Sách Chi Tiết Đề Tài Khối Y Tế (VMEC-01 đến VMEC-20)

Tài liệu tổng hợp chi tiết toàn bộ các đề tài thuộc **Khối Hệ Thống Y Tế (VMEC)** từ Ngân hàng đề tài AI20K.

---

## 1. [VMEC-01] AI Agent Trợ Lý Đặt Lịch Khám & Điều Hướng Chuyên Khoa Thông Minh (Ứng dụng y tế X)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-01`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân trên app Ứng dụng y tế X thường không biết mình nên khám chuyên khoa nào, đặt nhầm khoa, gọi tổng đài chờ lâu; lịch bác sĩ, phòng khám, khung giờ phân tán khiến việc đặt lịch nhiều bước thủ công.🎯 Vấn đề: Cần một AI Agent hội thoại tiếp nhận mô tả nhu cầu/triệu chứng bằng ngôn ngữ tự nhiên, tự lập kế hoạch nhiều bước (làm rõ nhu cầu → gợi ý chuyên khoa phù hợp → tra lịch trống bác sĩ → giữ chỗ → xác nhận đặt lịch → gửi nhắc), có memory nhớ hồ sơ và lịch sử khám để cá nhân hóa.🔒 Ràng buộc: HITL BẮT BUỘC — agent CHỈ gợi ý chuyên khoa/định hướng, KHÔNG chẩn đoán bệnh; mọi đặt lịch phải bệnh nhân xác nhận và lễ tân/điều phối duyệt trước khi chốt. Bảo mật PII/PHI (mã hóa, phân quyền theo vai trò). Luôn hiển thị khuyến cáo 'thông tin chỉ mang tính tham khảo, vui lòng gặp bác sĩ để được tư vấn chính xác'. Grounded trên danh mục chuyên khoa/dịch vụ Hệ thống y tế X (mô phỏng), chống bịa tên bác sĩ/khoa không tồn tại. Phát hiện dấu hiệu cấp cứu (đau ngực dữ dội, khó thở, đột quỵ) phải cảnh báo gọi 115/đến cấp cứu ngay thay vì đặt lịch thường.

### 🛠️ Tech Stack Gợi Ý
• LLM (GPT-4o/Claude/Gemini) qua API• LangGraph điều phối agent đa bước với state machine (làm rõ→tra lịch→giữ chỗ→xác nhận)• RAG trên danh mục chuyên khoa/dịch vụ/mô tả triệu chứng-khoa (nguồn nội bộ mô phỏng) + vector DB (Qdrant/Chroma/pgvector)• tool: booking API mô phỏng (query lịch trống, hold slot, confirm), calendar• guardrails (NeMo Guardrails/Guardrails AI) chặn chẩn đoán & lọc PII• backend FastAPI/Node• frontend Next.js/React + Tailwind, đăng nhập ≥2 vai trò (bệnh nhân, lễ tân/điều phối)• DB Postgres• deploy Vercel + Render/Railway (hoặc Docker trên cloud).

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• Web app deploy online, đăng nhập 2 vai trò (bệnh nhân/lễ tân)• agent hội thoại gợi ý chuyên khoa, tra lịch trống mô phỏng và đặt lịch có bước bệnh nhân xác nhận• hiển thị khuyến cáo y tế & phát hiện từ khóa cấp cứu• RAG có trích nguồn danh mục khoa.Nâng cao:• Memory hồ sơ bệnh nhân cá nhân hóa gợi ý• human-in-the-loop cho lễ tân duyệt/đổi lịch• xử lý xung đột lịch & đề xuất khung giờ thay thế• nhắc lịch tự động (email/thông báo)• dashboard điều phối theo dõi tỉ lệ đặt đúng khoa• log & cảnh báo khi agent không đủ tự tin (chuyển người thật).

---

## 2. [VMEC-02] AI Agent Phân Loại Triệu Chứng & Triage Thông Minh (Không Chẩn Đoán Thay Bác Sĩ)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-02`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Khi bệnh nhân mô tả triệu chứng qua app/hotline, việc phân luồng mức độ khẩn cấp (cấp cứu / khám sớm / tự theo dõi) phụ thuộc điều dưỡng trực, dễ quá tải và không đồng nhất.🎯 Vấn đề: Cần AI Agent triage thu thập triệu chứng theo kịch bản hỏi-đáp có cấu trúc, lập luận nhiều bước để phân loại mức độ ưu tiên và đề xuất hướng xử trí (đến cấp cứu / đặt lịch khám / chăm sóc tại nhà), có tool tra bảng phân độ và chuyển ca cho điều dưỡng khi vượt ngưỡng.🔒 Ràng buộc: HITL BẮT BUỘC — kết quả triage là ĐỀ XUẤT, điều dưỡng/bác sĩ phê duyệt trước khi thông báo hướng xử trí; AI TUYỆT ĐỐI KHÔNG kết luận chẩn đoán bệnh cụ thể. Grounded trên protocol triage chuẩn (mô phỏng theo hướng dẫn), chống bịa. Luôn ưu tiên an toàn: nghi ngờ red-flag (đau ngực, khó thở, dấu đột quỵ FAST, chảy máu nặng, co giật) → escalate cấp cứu ngay, cảnh báo rõ ràng. Bảo mật PII/PHI. Hiển thị giới hạn & khuyến cáo gặp nhân viên y tế.

### 🛠️ Tech Stack Gợi Ý
• LLM đa nhà cung cấp• LangGraph với nhánh điều kiện theo mức triage & node escalation• RAG trên bộ protocol/triage guideline mô phỏng + vector DB• guardrails chặn chẩn đoán/kê đơn, red-flag detector (rule + LLM)• tool: symptom questionnaire engine, phân độ ESI mô phỏng, hàng đợi điều dưỡng• backend FastAPI• frontend React/Next.js đăng nhập bệnh nhân & điều dưỡng• realtime (WebSocket) đẩy ca cho điều dưỡng• Postgres• deploy cloud (Docker/Vercel/Render).

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, 2 vai trò (bệnh nhân/điều dưỡng)• agent hỏi-đáp triage có cấu trúc, phân 3-4 mức ưu tiên kèm hướng xử trí đề xuất• phát hiện red-flag → cảnh báo cấp cứu• khuyến cáo & disclaimer rõ.Nâng cao:• Hàng đợi triage realtime cho điều dưỡng duyệt/điều chỉnh (HITL)• memory phiên & tổng hợp triệu chứng thành phiếu bàn giao• giải thích lý do phân độ có trích guideline• xử lý thông tin thiếu/mâu thuẫn bằng câu hỏi làm rõ• log kiểm toán & thống kê độ chính xác so với điều dưỡng.

---

## 3. [VMEC-03] AI Agent Tóm Tắt Bệnh Án & Hồ Sơ Sức Khỏe Đa Nguồn Cho Bác Sĩ

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-03`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh án một bệnh nhân trải dài nhiều lần khám, kết quả xét nghiệm, chẩn đoán hình ảnh, đơn thuốc; bác sĩ mất nhiều thời gian đọc lại toàn bộ trước mỗi lượt khám.🎯 Vấn đề: Cần AI Agent tổng hợp hồ sơ sức khỏe (mô phỏng, đa nguồn) thành bản tóm tắt lâm sàng có cấu trúc theo dòng thời gian: vấn đề chính, bệnh nền, thuốc đang dùng, xu hướng chỉ số, cảnh báo tương tác — agent phải lập kế hoạch truy xuất, đối chiếu và trích nguồn từng thông tin.🔒 Ràng buộc: HITL BẮT BUỘC — bản tóm tắt là hỗ trợ tham khảo, bác sĩ phải rà soát & xác nhận trước khi dùng ra quyết định; AI KHÔNG tự đưa ra chẩn đoán/điều trị mới. Grounded tuyệt đối trên dữ liệu hồ sơ, MỌI câu tóm tắt phải trích nguồn (lần khám/tài liệu), chống bịa số liệu. Bảo mật PHI nghiêm ngặt, phân quyền theo bác sĩ điều trị. Cảnh báo giới hạn khi dữ liệu thiếu/mâu thuẫn.

### 🛠️ Tech Stack Gợi Ý
• LLM ngữ cảnh dài• LangGraph điều phối retrieve→đối chiếu→tóm tắt→gắn nguồn• RAG trên EHR mô phỏng (JSON/FHIR-like) + vector DB, hybrid search• tool: truy vấn timeline, trích xuất chỉ số xét nghiệm, kiểm tra tương tác thuốc• guardrails chống bịa & buộc citation• backend FastAPI• frontend Next.js với view tóm tắt + panel nguồn gốc• đăng nhập bác sĩ/quản trị• Postgres + object store• deploy Docker/cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, đăng nhập bác sĩ/quản trị• nhập/chọn hồ sơ mô phỏng, agent sinh tóm tắt lâm sàng có cấu trúc + trích nguồn từng mục• disclaimer bác sĩ phải xác nhận.Nâng cao:• Timeline tương tác & biểu đồ xu hướng chỉ số• phát hiện & gắn cờ mâu thuẫn dữ liệu và tương tác thuốc• HITL để bác sĩ chỉnh sửa/duyệt tóm tắt lưu vào hồ sơ• memory theo bệnh nhân• xuất PDF bàn giao• audit log truy cập PHI.

---

## 4. [VMEC-04] AI Agent Nhắc Thuốc & Theo Dõi Tuân Thủ Điều Trị

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-04`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân, đặc biệt người cao tuổi và bệnh mạn tính, thường quên uống thuốc, uống sai liều/sai giờ, tự ý ngưng thuốc, làm giảm hiệu quả điều trị và tăng tái nhập viện.🎯 Vấn đề: Cần AI Agent quản lý phác đồ dùng thuốc (từ đơn mô phỏng do bác sĩ nhập), tự lập lịch nhắc thông minh, hội thoại xác nhận đã uống, phát hiện bỏ liều/tác dụng phụ, và chủ động cảnh báo cho người thân/điều dưỡng khi tuân thủ kém — agent lập kế hoạch thu thập→phân tích→giáo dục→escalate.🔒 Ràng buộc: HITL BẮT BUỘC — đơn thuốc/liều CHỈ do bác sĩ tạo và duyệt; AI KHÔNG tự kê, tự đổi liều hay khuyên ngưng thuốc; mọi thay đổi phác đồ phải bác sĩ phê duyệt. Grounded trên đơn đã duyệt & thông tin thuốc có nguồn, chống bịa liều/tương tác. Khi bệnh nhân báo tác dụng phụ nghiêm trọng → cảnh báo an toàn và chuyển bác sĩ/cấp cứu. Bảo mật PII/PHI. Luôn khuyến cáo hỏi bác sĩ/dược sĩ khi nghi ngờ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent với scheduler & vòng lặp theo dõi tuân thủ• RAG trên cơ sở dữ liệu thuốc mô phỏng (chỉ định, tác dụng phụ) + vector DB• tool: reminder/notification (email/web push), adherence tracker, escalation• guardrails chặn kê đơn/đổi liều• backend FastAPI + cron/Celery• frontend React/Next.js đăng nhập bệnh nhân, người thân, bác sĩ• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/bác sĩ, tùy chọn người thân)• bác sĩ nhập & duyệt phác đồ, agent tạo lịch nhắc, hội thoại xác nhận uống thuốc và ghi nhận• hiển thị khuyến cáo & không tự đổi liều.Nâng cao:• Dashboard tuân thủ (tỉ lệ, chuỗi bỏ liều) cho bác sĩ• cảnh báo tác dụng phụ nghiêm trọng → escalate• HITL để bác sĩ duyệt điều chỉnh lịch• memory thói quen bệnh nhân tối ưu giờ nhắc• báo cáo định kỳ• xử lý lỗi khi bệnh nhân không phản hồi (nhắc lại/báo người thân).

---

## 5. [VMEC-05] AI Agent Giải Thích Kết Quả Xét Nghiệm Bằng Ngôn Ngữ Dễ Hiểu Cho Bệnh Nhân

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-05`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân nhận phiếu kết quả xét nghiệm đầy chỉ số và thuật ngữ (WBC, HbA1c, LDL...) nhưng không hiểu ý nghĩa, lo lắng quá mức hoặc chủ quan, gọi hỏi bác sĩ/hotline nhiều.🎯 Vấn đề: Cần AI Agent tiếp nhận phiếu kết quả (mô phỏng), đối chiếu khoảng tham chiếu, giải thích từng chỉ số bằng ngôn ngữ đơn giản, nêu chỉ số bất thường và ý nghĩa chung, gợi ý câu hỏi nên hỏi bác sĩ — agent lập kế hoạch: phân tích → tra cứu chỉ số có nguồn → cá nhân hóa lời giải → tạo bản tóm tắt thân thiện.🔒 Ràng buộc: HITL & AN TOÀN — AI CHỈ giải thích thông tin chung, TUYỆT ĐỐI KHÔNG chẩn đoán bệnh, không kết luận nguyên nhân, không đề nghị điều trị; luôn khuyến cáo trao đổi bác sĩ để được diễn giải chính xác. Grounded trên khoảng tham chiếu & tài liệu giáo dục y khoa có nguồn, chống bịa. Chỉ số nguy hiểm (ví dụ đường huyết/kali cực đoan) → cảnh báo cần liên hệ y tế khẩn. Bảo mật PHI.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối parse→đối chiếu tham chiếu→giải thích→kiểm guardrail• RAG trên thư viện giải thích chỉ số/khoảng tham chiếu có nguồn + vector DB• tool: parser phiếu kết quả (JSON/CSV/OCR ảnh mô phỏng), reference-range checker, critical-value detector• guardrails chống chẩn đoán• backend FastAPI• frontend Next.js đăng nhập bệnh nhân/bác sĩ• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, đăng nhập bệnh nhân (và bác sĩ)• tải/chọn phiếu kết quả mô phỏng, agent giải thích từng chỉ số dễ hiểu, đánh dấu bất thường, có nguồn & disclaimer không chẩn đoán.Nâng cao:• OCR ảnh phiếu kết quả• phát hiện giá trị nguy kịch → cảnh báo khẩn• sinh danh sách câu hỏi cho bác sĩ• memory theo dõi xu hướng chỉ số qua các lần• HITL cho bác sĩ bổ sung ghi chú diễn giải• đa ngôn ngữ• log & giới hạn phạm vi khi gặp xét nghiệm ngoài thư viện.

---

## 6. [VMEC-06] AI Agent Trợ Lý Bác Sĩ Soạn Ghi Chú Lâm Sàng (Clinical Note SOAP)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-06`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bác sĩ tốn nhiều thời gian ghi chép bệnh án sau mỗi lượt khám, thường làm cuối ngày dễ sót thông tin, giảm thời gian cho bệnh nhân.🎯 Vấn đề: Cần AI Agent nhận nội dung hội thoại/ghi chú thô của buổi khám (văn bản hoặc thoại→text mô phỏng) và soạn ghi chú lâm sàng có cấu trúc SOAP (Subjective/Objective/Assessment/Plan), trích các chỉ số/thông tin đã nêu, gợi ý mã ICD tham khảo và các mục còn thiếu để bác sĩ bổ sung — agent lập kế hoạch trích xuất→cấu trúc hóa→kiểm tra thiếu sót→chờ duyệt.🔒 Ràng buộc: HITL BẮT BUỘC — ghi chú là BẢN NHÁP, bác sĩ phải rà soát, chỉnh và ký duyệt trước khi lưu; AI KHÔNG tự đưa chẩn đoán cuối hay chỉ định điều trị, chỉ tổng hợp từ dữ liệu bác sĩ cung cấp. Grounded trên nội dung buổi khám, chống bịa triệu chứng/chỉ số không được nêu (đánh dấu 'chưa ghi nhận'). Bảo mật PHI. Cảnh báo giới hạn & yêu cầu bác sĩ kiểm chứng mã ICD/thuật ngữ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối trích xuất→SOAP→gợi ý ICD→review• RAG trên bộ template SOAP & danh mục ICD-10 mô phỏng + vector DB• tool: ASR→text (mô phỏng/tùy chọn), ICD lookup, missing-field checker• guardrails chống bịa & buộc đánh dấu thông tin thiếu• backend FastAPI• frontend Next.js editor có track changes, đăng nhập bác sĩ/quản trị• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, đăng nhập bác sĩ• nhập ghi chú thô/transcript, agent sinh note SOAP có cấu trúc + đánh dấu mục thiếu• bác sĩ chỉnh & duyệt trước khi lưu• disclaimer bản nháp.Nâng cao:• Gợi ý mã ICD tham khảo có nguồn• ghi âm→text• HITL editor so sánh AI vs bản duyệt• memory mẫu ghi chú theo bác sĩ• kiểm tra nhất quán với hồ sơ trước• xuất PDF/bàn giao• audit log & cảnh báo khi thông tin không đủ để soạn.

---

## 7. [VMEC-07] AI Agent Quản Lý Bệnh Đái Tháo Đường & Theo Dõi Đường Huyết Tại Nhà

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-07`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân tiểu đường phải tự đo đường huyết, ghi nhật ký, điều chỉnh ăn uống/vận động; dữ liệu rời rạc, bác sĩ khó theo dõi giữa các lần tái khám.🎯 Vấn đề: Cần AI Agent theo dõi bệnh mạn tính: nhận số đo đường huyết/HbA1c, bữa ăn, vận động (mô phỏng bệnh nhân nhập), phân tích xu hướng, nhắc đo & tái khám, đưa lời khuyên lối sống chung theo phác đồ bác sĩ, và cảnh báo bác sĩ khi ngoài ngưỡng — agent lập kế hoạch thu thập→phân tích→giáo dục→escalate.🔒 Ràng buộc: HITL BẮT BUỘC — ngưỡng mục tiêu & mọi thay đổi thuốc/insulin do bác sĩ đặt và duyệt; AI KHÔNG tự chỉnh liều insulin, KHÔNG chẩn đoán biến chứng. Grounded trên hướng dẫn quản lý tiểu đường có nguồn & phác đồ bác sĩ, chống bịa. Đường huyết quá thấp/cao nguy hiểm (hạ đường huyết nặng, DKA) → cảnh báo xử trí khẩn & liên hệ y tế ngay. Bảo mật PHI. Luôn khuyến cáo tham vấn bác sĩ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent theo dõi định kỳ + node cảnh báo ngưỡng• RAG trên guideline ADA/Bộ Y tế mô phỏng + vector DB• tool: glucose log, trend/analytics, reminder, escalation• guardrails chặn chỉnh liều/chẩn đoán• backend FastAPI + scheduler• frontend Next.js biểu đồ xu hướng, đăng nhập bệnh nhân/bác sĩ• Postgres/time-series• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/bác sĩ)• nhập số đo & nhật ký, agent hiển thị xu hướng, nhắc đo/tái khám, lời khuyên lối sống chung có nguồn• phát hiện giá trị nguy hiểm → cảnh báo.Nâng cao:• Dashboard bác sĩ theo dõi nhiều bệnh nhân & gắn cờ ngoài ngưỡng (HITL duyệt lời khuyên)• dự báo xu hướng đơn giản• tích hợp dinh dưỡng/vận động• memory cá nhân hóa mục tiêu• báo cáo định kỳ cho lần tái khám• xử lý dữ liệu thiếu/bất thường.

---

## 8. [VMEC-08] AI Agent Theo Dõi & Quản Lý Tăng Huyết Áp Tại Nhà

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-08`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Người tăng huyết áp cần đo huyết áp đều đặn và duy trì lối sống, nhưng thường đo không đúng cách, ghi chép thất thường, không nhận ra xu hướng xấu đến khi có biến chứng.🎯 Vấn đề: Cần AI Agent quản lý huyết áp: hướng dẫn đo đúng, nhận chỉ số tâm thu/tâm trương & nhịp tim (mô phỏng), phân loại theo phân độ, phân tích xu hướng theo thời gian, nhắc đo/uống thuốc, giáo dục lối sống, và cảnh báo bác sĩ khi tăng huyết áp khẩn cấp — agent điều phối thu thập→phân loại→giáo dục→escalate.🔒 Ràng buộc: HITL BẮT BUỘC — ngưỡng & thuốc do bác sĩ đặt/duyệt; AI KHÔNG tự đổi thuốc, KHÔNG chẩn đoán nguyên nhân. Grounded trên hướng dẫn THA có nguồn, chống bịa. Cơn tăng huyết áp cấp cứu (>180/120 kèm triệu chứng, đau ngực, dấu đột quỵ) → cảnh báo đến cấp cứu/gọi 115 ngay. Bảo mật PHI. Khuyến cáo tham vấn bác sĩ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph với phân nhánh theo phân độ HA & node escalation• RAG trên guideline tăng huyết áp mô phỏng + vector DB• tool: BP log, trend analytics, reminder, hypertensive-crisis detector• guardrails chống đổi thuốc/chẩn đoán• backend FastAPI + scheduler• frontend Next.js biểu đồ, đăng nhập bệnh nhân/bác sĩ• Postgres/time-series• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò• nhập chỉ số HA, agent phân loại phân độ, hiển thị xu hướng, nhắc đo/thuốc, lời khuyên lối sống có nguồn• phát hiện cơn cấp cứu → cảnh báo khẩn.Nâng cao:• Dashboard bác sĩ đa bệnh nhân + gắn cờ• phát hiện đo sai/bất thường & hướng dẫn đo lại• HITL duyệt khuyến nghị• memory mục tiêu cá nhân• báo cáo tái khám• đa thiết bị/đa ngôn ngữ• xử lý lỗi dữ liệu.

---

## 9. [VMEC-09] AI Agent Giáo Dục Sức Khỏe Cá Nhân Hóa (Grounded, Có Nguồn)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-09`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân tìm thông tin sức khỏe trên mạng dễ gặp tin sai lệch, không phù hợp tình trạng cá nhân; nội dung giáo dục của bệnh viện dạng chung, ít cá nhân hóa.🎯 Vấn đề: Cần AI Agent giáo dục sức khỏe hỏi-đáp dựa trên thư viện nội dung y khoa đã kiểm duyệt (mô phỏng), cá nhân hóa theo hồ sơ (tuổi, bệnh nền, mối quan tâm), xây lộ trình học kiến thức theo chủ đề (dinh dưỡng, phòng bệnh, chăm sóc bệnh mạn tính), và luôn trích nguồn — agent lập kế hoạch truy xuất→cá nhân hóa→kiểm chứng→trả lời.🔒 Ràng buộc: AN TOÀN & GROUNDED — CHỈ trả lời từ thư viện đã duyệt, TỪ CHỐI/né các câu ngoài phạm vi hoặc yêu cầu chẩn đoán/kê đơn; AI KHÔNG chẩn đoán, KHÔNG thay tư vấn bác sĩ. Mọi câu trả lời trích nguồn, chống bịa thông tin y khoa. Phát hiện dấu hiệu nguy hiểm trong câu hỏi → khuyến cáo gặp bác sĩ/cấp cứu. Bảo mật PII. HITL cho biên tập viên y khoa duyệt nội dung mới.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối retrieve→cá nhân hóa→citation→guardrail• RAG chặt trên thư viện nội dung y khoa duyệt + vector DB, reranker• tool: personalization theo hồ sơ, learning-path builder, out-of-scope detector• guardrails buộc grounding & từ chối ngoài phạm vi• backend FastAPI• frontend Next.js đăng nhập bệnh nhân & biên tập viên y khoa• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/biên tập viên)• Q&A giáo dục sức khỏe grounded có trích nguồn, cá nhân hóa cơ bản theo hồ sơ• từ chối câu ngoài phạm vi & disclaimer.Nâng cao:• Lộ trình học theo chủ đề & theo dõi tiến độ• memory sở thích/lịch sử• HITL cho biên tập viên thêm/duyệt nội dung vào thư viện• phát hiện & xử lý câu hỏi nguy hiểm• đánh giá kiến thức (quiz)• đa ngôn ngữ• log câu hỏi ngoài phạm vi để mở rộng thư viện.

---

## 10. [VMEC-10] AI Agent Trợ Lý Dinh Dưỡng & Lối Sống Theo Bệnh Lý

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-10`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân cần chế độ ăn phù hợp bệnh lý (tiểu đường, thận, tim mạch, gout) và mục tiêu cân nặng, nhưng khó tự lập thực đơn cân đối, dễ theo lời khuyên thiếu căn cứ.🎯 Vấn đề: Cần AI Agent dinh dưỡng: nhận hồ sơ & ràng buộc ăn kiêng (mô phỏng), gợi ý thực đơn/khẩu phần theo nguyên tắc dinh dưỡng lâm sàng, ước tính năng lượng/đường/muối, ghi nhật ký ăn uống và phản hồi điều chỉnh, đồng bộ mục tiêu do bác sĩ/dinh dưỡng đặt — agent lập kế hoạch: phân tích nhu cầu→tra CSDL thực phẩm→sinh thực đơn→theo dõi.🔒 Ràng buộc: HITL BẮT BUỘC — kế hoạch dinh dưỡng cho bệnh nhân bệnh lý phải chuyên gia dinh dưỡng/bác sĩ duyệt; AI KHÔNG tự kê chế độ điều trị y khoa, KHÔNG chẩn đoán. Grounded trên bảng thành phần thực phẩm & guideline dinh dưỡng có nguồn, chống bịa số liệu calo/dinh dưỡng. Cảnh báo dị ứng & tương tác thực phẩm-thuốc. Bảo mật PII/PHI. Luôn khuyến cáo tham vấn chuyên gia.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối tính nhu cầu→truy vấn thực phẩm→lập thực đơn→theo dõi• RAG trên bảng thành phần thực phẩm VN & guideline dinh dưỡng mô phỏng + vector DB• tool: nutrition calculator, meal planner, food log, allergy/interaction checker• guardrails chống bịa & chặn chỉ định y khoa• backend FastAPI• frontend Next.js đăng nhập bệnh nhân & chuyên gia dinh dưỡng• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/dinh dưỡng)• nhập hồ sơ & ràng buộc, agent gợi ý thực đơn kèm ước tính dinh dưỡng có nguồn, nhật ký ăn uống• disclaimer & cảnh báo dị ứng.Nâng cao:• HITL cho chuyên gia duyệt/chỉnh thực đơn• phân tích xu hướng dinh dưỡng theo mục tiêu• cảnh báo vượt ngưỡng muối/đường theo bệnh lý• memory sở thích & thực phẩm sẵn có• tạo danh sách đi chợ• đồng bộ với mục tiêu bác sĩ• xử lý thực phẩm ngoài CSDL.

---

## 11. [VMEC-11] AI Agent Hỗ Trợ Điều Dưỡng & Phân Luồng Bệnh Nhân Nội Trú

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-11`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Điều dưỡng quản lý nhiều bệnh nhân nội trú với dấu hiệu sinh tồn, y lệnh, lịch chăm sóc; ghi chép và ưu tiên hóa công việc thủ công dễ quá tải, sót y lệnh.🎯 Vấn đề: Cần AI Agent hỗ trợ điều dưỡng: tổng hợp danh sách bệnh nhân & vital signs (mô phỏng), tính điểm cảnh báo sớm (EWS), sắp xếp thứ tự ưu tiên chăm sóc, nhắc y lệnh/thuốc theo giờ, và tạo bàn giao ca — agent lập kế hoạch giám sát→ưu tiên hóa→nhắc→bàn giao, có tool đọc vital & escalation.🔒 Ràng buộc: HITL BẮT BUỘC — mọi cảnh báo/ưu tiên là ĐỀ XUẤT hỗ trợ, điều dưỡng/bác sĩ quyết định; AI KHÔNG tự ra y lệnh, KHÔNG chẩn đoán, KHÔNG đổi thuốc. Grounded trên y lệnh & protocol điều dưỡng mô phỏng, chống bịa. Điểm EWS cao/dấu hiệu xấu đi → cảnh báo bác sĩ ngay. Bảo mật PHI, phân quyền theo ca/khoa. Cảnh báo giới hạn.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent giám sát định kỳ + node escalation theo EWS• RAG trên protocol điều dưỡng & danh mục y lệnh mô phỏng + vector DB• tool: vital ingest, EWS calculator, task prioritizer, shift-handover generator, alerting• guardrails chống ra y lệnh• backend FastAPI + WebSocket• frontend Next.js dashboard điều dưỡng, đăng nhập điều dưỡng/bác sĩ• Postgres/time-series• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (điều dưỡng/bác sĩ)• dashboard bệnh nhân với vital & EWS, agent ưu tiên hóa công việc và nhắc y lệnh theo giờ• cảnh báo EWS cao• disclaimer hỗ trợ.Nâng cao:• Sinh báo cáo bàn giao ca tự động (HITL điều dưỡng duyệt)• realtime cảnh báo xấu đi → escalate bác sĩ• memory theo bệnh nhân/ca• phát hiện y lệnh sắp trễ• thống kê tải công việc• xử lý dữ liệu vital thiếu/bất thường.

---

## 12. [VMEC-12] AI Agent Tra Cứu Tương Tác Thuốc & Cảnh Báo An Toàn Dùng Thuốc

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-12`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân dùng nhiều thuốc (đa bệnh, đơn từ nhiều nơi, thực phẩm chức năng) dễ gặp tương tác nguy hiểm; việc tra cứu thủ công tốn thời gian và không đầy đủ.🎯 Vấn đề: Cần AI Agent kiểm tra an toàn thuốc: nhận danh sách thuốc đang dùng (mô phỏng, gồm cả OTC/thực phẩm chức năng), tra tương tác thuốc-thuốc và thuốc-thực phẩm, cảnh báo mức độ nghiêm trọng, giải thích dễ hiểu và gợi ý trao đổi bác sĩ/dược sĩ — agent lập kế hoạch chuẩn hóa tên thuốc→tra tương tác→xếp mức độ→giải thích có nguồn.🔒 Ràng buộc: HITL & AN TOÀN — kết quả là CẢNH BÁO tham khảo, quyết định thay đổi thuốc do bác sĩ/dược sĩ; AI KHÔNG tự khuyên ngưng/đổi/kê thuốc, KHÔNG chẩn đoán. Grounded tuyệt đối trên CSDL tương tác thuốc có nguồn, chống bịa tương tác/liều. Tương tác mức nghiêm trọng → cảnh báo nổi bật & khuyến cáo liên hệ y tế ngay. Bảo mật PII/PHI. Nêu rõ giới hạn dữ liệu.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối chuẩn hóa→tra cứu→xếp hạng→giải thích• RAG trên CSDL thuốc & tương tác mô phỏng (dựa cấu trúc kiểu DrugBank/RxNorm) + vector DB• tool: drug-name normalizer, interaction lookup, severity ranker• guardrails chặn khuyên đổi thuốc & buộc citation• backend FastAPI• frontend Next.js đăng nhập bệnh nhân & dược sĩ/bác sĩ• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/dược sĩ)• nhập danh sách thuốc, agent phát hiện & xếp mức tương tác kèm giải thích có nguồn• cảnh báo nghiêm trọng & disclaimer không tự đổi thuốc.Nâng cao:• Chuẩn hóa tên thuốc mờ/viết tắt• tương tác thuốc-thực phẩm & thuốc-bệnh nền• HITL cho dược sĩ xác nhận/ghi chú• memory hồ sơ thuốc bệnh nhân• quét đơn ảnh (OCR)• cảnh báo trùng hoạt chất• xử lý thuốc ngoài CSDL (nêu giới hạn).

---

## 13. [VMEC-13] AI Agent Trợ Lý Tiền Sản Cho Thai Phụ (Theo Dõi Thai Kỳ)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-13`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Thai phụ có nhiều thắc mắc theo từng tuần thai, lịch khám/xét nghiệm/tiêm phòng phức tạp, dễ bỏ mốc quan trọng và lo lắng về dấu hiệu bất thường.🎯 Vấn đề: Cần AI Agent tiền sản: cá nhân hóa theo tuổi thai (mô phỏng), nhắc lịch khám/siêu âm/xét nghiệm/tiêm theo mốc, giáo dục kiến thức thai kỳ có nguồn, ghi nhận triệu chứng & cân nặng/HA, và cảnh báo dấu hiệu nguy hiểm cần đi khám ngay — agent lập kế hoạch theo timeline thai kỳ→nhắc→giáo dục→sàng lọc dấu hiệu.🔒 Ràng buộc: HITL & AN TOÀN — AI CHỈ giáo dục & nhắc lịch, KHÔNG chẩn đoán, KHÔNG thay khám thai; mọi lo ngại y khoa chuyển bác sĩ sản. Grounded trên tài liệu chăm sóc thai kỳ có nguồn, chống bịa. Dấu hiệu nguy hiểm (ra máu, đau bụng dữ dội, giảm cử động thai, phù/đau đầu/mờ mắt nghi tiền sản giật) → cảnh báo đến cơ sở y tế ngay. Bảo mật PHI. Khuyến cáo tham vấn bác sĩ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent theo timeline thai kỳ + node sàng lọc red-flag• RAG trên tài liệu tiền sản/lịch khám chuẩn mô phỏng + vector DB• tool: pregnancy-week scheduler, reminder, symptom screener, danger-sign detector• guardrails chống chẩn đoán• backend FastAPI + scheduler• frontend Next.js đăng nhập thai phụ & bác sĩ sản• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (thai phụ/bác sĩ)• cá nhân hóa theo tuần thai, nhắc mốc khám/xét nghiệm/tiêm, Q&A giáo dục có nguồn• sàng lọc dấu hiệu nguy hiểm → cảnh báo• disclaimer.Nâng cao:• Nhật ký cân nặng/HA/cử động thai & biểu đồ• HITL cho bác sĩ theo dõi & duyệt nhắc• memory theo thai kỳ• nội dung theo tam cá nguyệt• danh sách câu hỏi cho lần khám• đa ngôn ngữ• xử lý ngày dự sinh thay đổi.

---

## 14. [VMEC-14] AI Agent Trợ Lý Nhi Khoa Cho Phụ Huynh (Theo Dõi Sức Khỏe Trẻ)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-14`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Phụ huynh lo lắng khi con ốm, khó nhớ lịch tiêm chủng và mốc phát triển, dễ tìm thông tin sai và tự ý dùng thuốc cho trẻ.🎯 Vấn đề: Cần AI Agent nhi khoa: quản lý hồ sơ trẻ (mô phỏng), nhắc lịch tiêm chủng & khám định kỳ theo tuổi, theo dõi tăng trưởng (cân nặng/chiều cao theo biểu đồ percentile), giáo dục chăm sóc trẻ & xử trí triệu chứng thường gặp có nguồn, và sàng lọc dấu hiệu nguy hiểm — agent lập kế hoạch theo tuổi trẻ→nhắc→giáo dục→sàng lọc.🔒 Ràng buộc: HITL & AN TOÀN — AI CHỈ hướng dẫn chung & nhắc lịch, KHÔNG chẩn đoán, KHÔNG khuyên liều thuốc cụ thể cho trẻ (đặc biệt hạ sốt/kháng sinh) — chuyển bác sĩ nhi. Grounded trên lịch tiêm chủng & tài liệu nhi khoa có nguồn, chống bịa. Dấu hiệu nguy hiểm ở trẻ (sốt cao co giật, khó thở, li bì, mất nước nặng, phát ban nghi nặng) → cảnh báo đưa trẻ đi khám/cấp cứu ngay. Bảo mật PHI của trẻ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent theo tuổi trẻ + node red-flag nhi• RAG trên lịch tiêm chủng, biểu đồ tăng trưởng WHO, tài liệu nhi mô phỏng + vector DB• tool: vaccination scheduler, growth-percentile calculator, symptom screener, danger-sign detector• guardrails chặn liều thuốc/chẩn đoán• backend FastAPI + scheduler• frontend Next.js đăng nhập phụ huynh & bác sĩ nhi• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (phụ huynh/bác sĩ nhi)• hồ sơ trẻ, nhắc lịch tiêm & khám, biểu đồ tăng trưởng percentile, Q&A chăm sóc có nguồn• sàng lọc dấu hiệu nguy hiểm → cảnh báo• disclaimer không khuyên liều.Nâng cao:• Nhắc theo phác đồ tiêm nhiều mũi & bù mũi trễ• HITL cho bác sĩ theo dõi/duyệt• memory nhiều trẻ• mốc phát triển theo tuổi• nhật ký triệu chứng khi ốm• đa ngôn ngữ• xử lý dữ liệu tăng trưởng bất thường.

---

## 15. [VMEC-15] AI Agent Đặt & Quản Lý Gói Khám Sức Khỏe Định Kỳ (Health Check-up)

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-15`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Hệ thống y tế X có nhiều gói khám sức khỏe tổng quát/tầm soát; khách hàng khó chọn gói phù hợp độ tuổi/giới/tiền sử, và quy trình đặt gói kèm chuẩn bị (nhịn ăn, hồ sơ) dễ nhầm lẫn.🎯 Vấn đề: Cần AI Agent tư vấn & quản lý gói khám: hỏi nhu cầu/độ tuổi/yếu tố nguy cơ (mô phỏng), gợi ý gói phù hợp có so sánh, đặt lịch gói, hướng dẫn chuẩn bị trước khám, nhắc lịch và theo dõi hoàn thành các hạng mục trong gói — agent lập kế hoạch tư vấn→so sánh gói→đặt→hướng dẫn→theo dõi.🔒 Ràng buộc: HITL — gợi ý gói mang tính tham khảo, tư vấn viên/bác sĩ có thể điều chỉnh; AI KHÔNG chẩn đoán, KHÔNG chỉ định thêm xét nghiệm ngoài gói mà không có bác sĩ. Grounded trên danh mục gói & giá dịch vụ Hệ thống y tế X (mô phỏng), chống bịa gói/giá/hạng mục không có. Bảo mật PII/PHI. Khuyến cáo tham vấn bác sĩ để cá nhân hóa tầm soát. Phát hiện triệu chứng cấp → hướng đi khám thay vì chỉ khám định kỳ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối thu thập nhu cầu→match gói→booking→chuẩn bị→theo dõi• RAG trên catalog gói khám & hướng dẫn chuẩn bị mô phỏng + vector DB• tool: package recommender, booking API mô phỏng, prep-checklist, reminder• guardrails chống bịa & chặn chỉ định• backend FastAPI• frontend Next.js đăng nhập khách hàng & tư vấn viên• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (khách hàng/tư vấn viên)• agent tư vấn & so sánh gói theo nhu cầu, đặt lịch gói có xác nhận, hướng dẫn chuẩn bị• grounded trên catalog & disclaimer.Nâng cao:• Theo dõi hoàn thành hạng mục trong gói & nhắc mục còn thiếu• HITL cho tư vấn viên điều chỉnh gợi ý• memory tiền sử để cá nhân hóa tầm soát• gợi ý gói theo yếu tố nguy cơ• tổng hợp kết quả sau khám (liên kết đề giải thích kết quả)• xử lý gói hết chỗ/đổi lịch.

---

## 16. [VMEC-16] AI Agent Hỗ Trợ Chăm Sóc Sau Xuất Viện & Phòng Tái Nhập Viện

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-16`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Sau xuất viện, bệnh nhân thường không tuân thủ hướng dẫn chăm sóc, quên tái khám, không nhận ra biến chứng sớm dẫn đến tái nhập viện — chi phí cao và rủi ro.🎯 Vấn đề: Cần AI Agent chăm sóc sau xuất viện: nhận kế hoạch xuất viện (mô phỏng: thuốc, chăm sóc vết mổ, dấu hiệu cảnh báo, lịch tái khám), theo dõi bằng check-in định kỳ, nhắc thuốc & tái khám, thu thập triệu chứng phục hồi và sàng lọc biến chứng, escalate điều dưỡng/bác sĩ khi cần — agent lập kế hoạch theo lộ trình hồi phục→check-in→sàng lọc→escalate.🔒 Ràng buộc: HITL BẮT BUỘC — kế hoạch xuất viện do bác sĩ lập; AI CHỈ theo dõi & nhắc, KHÔNG chẩn đoán biến chứng, KHÔNG đổi thuốc; nghi biến chứng → chuyển nhân viên y tế. Grounded trên kế hoạch xuất viện & tài liệu chăm sóc có nguồn, chống bịa. Dấu hiệu nguy hiểm (sốt cao, vết mổ nhiễm trùng, đau ngực/khó thở, chảy máu) → cảnh báo liên hệ y tế/cấp cứu ngay. Bảo mật PHI.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph agent theo lộ trình hồi phục + node escalation• RAG trên hướng dẫn chăm sóc sau xuất viện mô phỏng + vector DB• tool: care-plan tracker, scheduled check-in, symptom/complication screener, reminder, escalation• guardrails chống chẩn đoán/đổi thuốc• backend FastAPI + scheduler• frontend Next.js đăng nhập bệnh nhân & điều dưỡng/bác sĩ• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/điều dưỡng)• nhập kế hoạch xuất viện, agent check-in định kỳ, nhắc thuốc & tái khám, thu thập triệu chứng• sàng lọc biến chứng → cảnh báo• disclaimer.Nâng cao:• Dashboard theo dõi nhóm bệnh nhân sau xuất viện & gắn cờ rủi ro tái nhập viện (HITL điều dưỡng duyệt/gọi lại)• hướng dẫn chăm sóc vết mổ theo ngày• memory lộ trình cá nhân• báo cáo hồi phục cho lần tái khám• xử lý bệnh nhân không phản hồi (nhắc lại/báo y tế).

---

## 17. [VMEC-17] AI Agent Phân Tích Phản Hồi Bệnh Nhân & Cải Tiến Chất Lượng Dịch Vụ

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-17`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Hệ thống y tế X nhận lượng lớn phản hồi bệnh nhân (khảo sát, đánh giá, góp ý) qua nhiều kênh; việc đọc, phân loại và phát hiện vấn đề dịch vụ thủ công chậm và bỏ sót phản hồi khẩn.🎯 Vấn đề: Cần AI Agent phân tích phản hồi (dữ liệu mô phỏng): tự phân loại chủ đề (chờ đợi, thái độ, viện phí, chuyên môn), phân tích cảm xúc, trích vấn đề & đề xuất hành động cải tiến, phát hiện phản hồi nghiêm trọng/khiếu nại khẩn để chuyển bộ phận liên quan, và tạo báo cáo insight cho quản lý — agent lập kế hoạch thu thập→phân loại→phân tích→cảnh báo→báo cáo.🔒 Ràng buộc: HITL — insight & phân loại là hỗ trợ, quản lý chất lượng ra quyết định hành động; AI KHÔNG tự phản hồi bệnh nhân thay bệnh viện. Grounded trên nội dung phản hồi thực (mô phỏng), chống bịa/quy chụp; trích dẫn phản hồi gốc. Bảo mật PII trong phản hồi (ẩn danh khi phân tích). Phản hồi liên quan an toàn người bệnh/sự cố y khoa → cảnh báo ưu tiên chuyển đúng bộ phận. Nêu giới hạn khi mẫu nhỏ.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối ingest→phân loại→sentiment→trích vấn đề→cảnh báo→báo cáo• RAG trên khung phân loại chủ đề & lịch sử phản hồi mô phỏng + vector DB (phát hiện chủ đề nổi)• tool: classifier, sentiment analyzer, PII redactor, alert router, report generator• guardrails chống quy chụp & buộc trích dẫn• backend FastAPI• frontend Next.js dashboard, đăng nhập nhân viên CSKH & quản lý chất lượng• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (CSKH/quản lý)• nhập/nạp phản hồi mô phỏng, agent phân loại chủ đề + cảm xúc, trích vấn đề chính có trích dẫn gốc• dashboard tổng quan• ẩn danh PII.Nâng cao:• Phát hiện chủ đề mới nổi & xu hướng theo thời gian• cảnh báo phản hồi nghiêm trọng → định tuyến đúng bộ phận (HITL duyệt hành động)• đề xuất hành động cải tiến ưu tiên hóa• báo cáo insight định kỳ tự động• so sánh theo khoa/kênh• xử lý phản hồi đa ngôn ngữ/ngắn.

---

## 18. [VMEC-18] AI Agent Trợ Lý Hành Chính Y Tế: Bảo Hiểm & Thanh Toán Viện Phí

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-18`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Bệnh nhân bối rối với thủ tục bảo hiểm (BHYT/bảo hiểm tư), quyền lợi chi trả, ước tính viện phí, hồ sơ cần chuẩn bị; nhân viên hành chính giải đáp lặp lại nhiều và dễ sai sót.🎯 Vấn đề: Cần AI Agent hành chính y tế: hỏi-đáp về quyền lợi bảo hiểm & quy trình thanh toán (mô phỏng), ước tính chi phí dịch vụ theo mức đồng chi trả, kiểm tra hồ sơ cần thiết, hướng dẫn nộp yêu cầu bồi thường và tra cứu trạng thái — agent lập kế hoạch xác định loại BH→tra quyền lợi→ước tính→lập checklist hồ sơ→theo dõi.🔒 Ràng buộc: HITL — thông tin quyền lợi/ước tính mang tính tham khảo, nhân viên bảo hiểm/tài chính xác nhận con số cuối; AI KHÔNG cam kết chi trả, KHÔNG tư vấn y khoa/chẩn đoán. Grounded trên chính sách bảo hiểm & bảng giá dịch vụ mô phỏng, chống bịa quyền lợi/số tiền/điều khoản. Bảo mật PII/PHI & thông tin tài chính. Nêu rõ ước tính có thể thay đổi và giới hạn dữ liệu.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối phân loại BH→tra chính sách→tính ước tính→checklist→tra trạng thái• RAG trên chính sách bảo hiểm, bảng giá, quy trình mô phỏng + vector DB• tool: cost estimator, coverage checker, document-checklist, claim-status lookup• guardrails buộc grounding & chống cam kết chi trả• backend FastAPI• frontend Next.js đăng nhập bệnh nhân & nhân viên hành chính/bảo hiểm• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (bệnh nhân/nhân viên hành chính)• Q&A quyền lợi bảo hiểm & thanh toán grounded có nguồn, ước tính chi phí dịch vụ, checklist hồ sơ• disclaimer ước tính tham khảo.Nâng cao:• Tra cứu & theo dõi trạng thái yêu cầu bồi thường• HITL cho nhân viên xác nhận/điều chỉnh ước tính• memory hồ sơ & loại bảo hiểm của bệnh nhân• giải thích khoản mục hóa đơn• phát hiện thiếu giấy tờ• xử lý nhiều loại bảo hiểm & cảnh báo khi ngoài phạm vi chính sách.

---

## 19. [VMEC-19] AI Agent Hỗ Trợ Tầm Soát Ung Thư & Nhắc Khám Sàng Lọc Định Kỳ

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-19`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Nhiều người bỏ lỡ tầm soát ung thư định kỳ (vú, cổ tử cung, đại trực tràng, gan, phổi) dù thuộc nhóm nguy cơ; kiến thức về mốc & phương pháp tầm soát còn hạn chế.🎯 Vấn đề: Cần AI Agent tầm soát: đánh giá yếu tố nguy cơ qua bộ câu hỏi (mô phỏng: tuổi, giới, tiền sử gia đình, lối sống), gợi ý loại & mốc tầm soát phù hợp theo hướng dẫn, đặt lịch tầm soát, giáo dục về dấu hiệu cảnh báo, và nhắc tái tầm soát định kỳ — agent lập kế hoạch đánh giá nguy cơ→khuyến nghị tầm soát→đặt lịch→nhắc định kỳ.🔒 Ràng buộc: HITL & AN TOÀN — đánh giá nguy cơ & khuyến nghị mang tính giáo dục/tham khảo, bác sĩ quyết định chỉ định tầm soát cụ thể; AI TUYỆT ĐỐI KHÔNG chẩn đoán ung thư, KHÔNG diễn giải kết quả tầm soát thay bác sĩ. Grounded trên hướng dẫn tầm soát ung thư có nguồn, chống bịa. Triệu chứng nghi ngờ (khối u, chảy máu bất thường, sụt cân nhanh) → khuyến cáo đi khám sớm, không trấn an sai. Bảo mật PHI. Truyền thông cẩn trọng, tránh gây hoảng loạn.

### 🛠️ Tech Stack Gợi Ý
• LLM• LangGraph điều phối đánh giá nguy cơ→khuyến nghị→đặt lịch→nhắc• RAG trên guideline tầm soát ung thư (theo tuổi/nguy cơ) mô phỏng + vector DB• tool: risk-assessment questionnaire, screening recommender, booking mô phỏng, recall reminder, red-flag detector• guardrails chống chẩn đoán & truyền thông an toàn• backend FastAPI + scheduler• frontend Next.js đăng nhập người dùng & bác sĩ• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (người dùng/bác sĩ)• bộ câu hỏi đánh giá nguy cơ, agent gợi ý loại & mốc tầm soát có nguồn, đặt lịch & giáo dục dấu hiệu• sàng lọc triệu chứng nghi ngờ → khuyến cáo• disclaimer không chẩn đoán.Nâng cao:• Lịch tái tầm soát cá nhân hóa & nhắc định kỳ dài hạn• HITL cho bác sĩ duyệt khuyến nghị & chỉ định• memory tiền sử/nguy cơ• theo dõi hoàn thành tầm soát• nội dung truyền thông theo loại ung thư• xử lý nhóm nguy cơ cao (chuyển bác sĩ chuyên khoa).

---

## 20. [VMEC-20] AI Agent Trợ Lý Sức Khỏe Tinh Thần Với Cảnh Báo An Toàn & Khủng Hoảng

- **Khối**: Hệ thống y tế X – App Ứng dụng y tế X (AI y tế)
- **Mã Đề**: `VMEC-20`
- **Quy mô nhóm tối đa**: 2 người

### 📌 Mô Tả Bài Toán & Ràng Buộc
📍 Thực trạng: Nhu cầu hỗ trợ sức khỏe tinh thần (stress, lo âu, mất ngủ, trầm cảm nhẹ) tăng, nhất là ở sinh viên & người mới đi làm, nhưng nguồn lực chuyên gia hạn chế và rào cản tìm kiếm hỗ trợ lớn.🎯 Vấn đề: Cần AI Agent đồng hành sức khỏe tinh thần: hội thoại hỗ trợ tâm lý dựa kỹ thuật tự chăm sóc có kiểm chứng (thở, CBT nền tảng, nhật ký cảm xúc — mô phỏng), sàng lọc tâm trạng định kỳ (thang PHQ-9/GAD-7 mô phỏng), gợi ý bài tập & tài nguyên, và đặc biệt phát hiện dấu hiệu khủng hoảng để kích hoạt quy trình an toàn — agent lập kế hoạch lắng nghe→sàng lọc→hỗ trợ tự chăm sóc→escalate khi cần.🔒 Ràng buộc: HITL & AN TOÀN LÀ TỐI THƯỢNG — AI KHÔNG chẩn đoán rối loạn tâm thần, KHÔNG thay trị liệu/kê thuốc; là hỗ trợ ban đầu, luôn khuyến khích gặp chuyên gia. Grounded trên tài liệu tâm lý có kiểm chứng, chống bịa. Phát hiện ý tưởng tự hại/tự tử hoặc nguy cơ → NGAY LẬP TỨC hiển thị đường dây nóng khủng hoảng, quy trình an toàn và chuyển kết nối chuyên gia/người thân (HITL bắt buộc). Bảo mật PII/PHI tuyệt đối, giọng điệu đồng cảm, không phán xét. Nêu rõ giới hạn của AI.

### 🛠️ Tech Stack Gợi Ý
• LLM (được prompt & guardrail an toàn nghiêm ngặt)• LangGraph với node sàng lọc khủng hoảng ưu tiên cao & escalation bắt buộc• RAG trên tài liệu CBT/tự chăm sóc & tài nguyên hỗ trợ có nguồn + vector DB• tool: mood screener (PHQ-9/GAD-7 mô phỏng), self-help exercise library, crisis-keyword detector, hotline/escalation router• guardrails chống chẩn đoán & bộ lọc an toàn khủng hoảng nhiều lớp• backend FastAPI• frontend Next.js đăng nhập người dùng & chuyên gia/điều phối• Postgres• deploy cloud.

### 🎯 Yêu Cầu Đầu Ra (Cơ Bản & Nâng Cao)
Cơ bản:• App deploy, ≥2 vai trò (người dùng/chuyên gia)• hội thoại hỗ trợ đồng cảm với bài tập tự chăm sóc có nguồn, sàng lọc tâm trạng định kỳ• phát hiện khủng hoảng → hiển thị đường dây nóng & quy trình an toàn• disclaimer & giới hạn rõ ràng.Nâng cao:• Nhật ký cảm xúc & theo dõi xu hướng tâm trạng• HITL cho chuyên gia nhận cảnh báo & tiếp nhận ca khủng hoảng• memory phiên đồng hành (an toàn, ẩn danh)• thư viện bài tập cá nhân hóa• kết nối người thân khẩn cấp (có đồng ý)• kiểm thử & log riêng cho kịch bản an toàn• đa lớp phát hiện nguy cơ giảm bỏ sót.

---


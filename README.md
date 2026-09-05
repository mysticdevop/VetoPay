# VetoPay — Autonomous Chargeback & Friendly-Fraud Defense Agent
*Razorpay AI Buildathon — Track 02: AI Risk Manager*

VetoPay protects merchants from loss due to friendly fraud, delivery disputes, and unnecessary bank representment penalties. It programmatically isolates winnable disputes backed by 3D-Secure logs and delivery OTP verifications, while immediately conceding lost disputes to save fee overhead.

---

### Quickstart

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the evaluation benchmark on 100 test cases:**
   ```bash
   python evaluation/run_eval.py
   ```

3. **Start the API service:**
   ```bash
   uvicorn src.api:app --reload --port 8000
   ```

4. **Verify via interactive API docs:**
   Navigate to `http://127.0.0.1:8000/docs`.
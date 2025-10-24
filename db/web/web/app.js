const API = "http://127.0.0.1:5000";

async function addEmployee() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const department = document.getElementById("dept").value.trim();
  const start_date = document.getElementById("start").value;
  const msg = document.getElementById("msg");

  try {
    const res = await fetch(`${API}/employees`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ name, email, department, start_date })
    });
    const data = await res.json();
    msg.textContent = res.ok ? `Created employee #${data.id}` : (data.error || "Failed");
    loadEmployees();
  } catch (e) {
    msg.textContent = "Request failed";
  }
}

async function loadEmployees() {
  const out = document.getElementById("list");
  const res = await fetch(`${API}/employees`);
  const data = await res.json();
  out.textContent = JSON.stringify(data, null, 2);
}

async function setStatus() {
  const id = Number(document.getElementById("empId").value);
  const status = document.getElementById("status").value;
  await fetch(`${API}/employees/status`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ id, status })
  });
  loadEmployees();
}

loadEmployees();

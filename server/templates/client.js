// frontend/client.js

document.addEventListener("DOMContentLoaded", () => {
  // Fetch active task count on page load
  updateTaskCount();

  // If the form exists on the page, handle its submission
  const form = document.getElementById("task-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const resultDiv = document.getElementById("form-result");

      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value.trim();
      const avgWpm = parseInt(document.getElementById("avg_wpm").value);
      const minAcc = parseInt(document.getElementById("min_accuracy").value);
      const races = parseInt(document.getElementById("races").value);
      const key = document.getElementById("key").value.trim();

      const payload = {
        username,
        password,
        avg_wpm: avgWpm,
        min_accuracy: minAcc,
        races,
        key
      };

      resultDiv.innerHTML = "Submitting task...";
      resultDiv.style.color = "#cccccc";

      try {
        const response = await fetch("/api/tasks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
          resultDiv.innerHTML = `✅ Task submitted! ID: <code>${data.task_id}</code>`;
          resultDiv.style.color = "lime";
          form.reset();
          updateTaskCount();
        } else {
          resultDiv.innerHTML = `❌ ${data.message || "Task submission failed."}`;
          resultDiv.style.color = "red";
        }
      } catch (error) {
        resultDiv.innerHTML = `❌ Error submitting task.`;
        resultDiv.style.color = "red";
        console.error("Form submit error:", error);
      }
    });
  }
});

async function updateTaskCount() {
  const counter = document.getElementById("active-counter");
  if (!counter) return;

  try {
    const res = await fetch("/api/tasks/active-count");
    const data = await res.json();
    counter.textContent = data.active_count || 0;
  } catch (err) {
    counter.textContent = "Error";
    console.error("Failed to fetch active task count:", err);
  }
}


const form = document.getElementById("summarize-form");
const output = document.getElementById("output");
const apiPrefix = document.body.getAttribute("data-api-prefix") || "";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  output.textContent = "Generating summary...";

  const formData = new FormData(form);

  try {
    const response = await fetch(`${apiPrefix}/api/summarize`, {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      output.textContent = `Error: ${payload.error || "Unable to summarize."}`;
      return;
    }
    output.textContent = payload.summary;
  } catch (error) {
    output.textContent = "Error: Network issue while contacting the server.";
  }
});

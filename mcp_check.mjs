import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

async function main() {
  const url = "https://phantom-cloud-engine.fly.dev/sse/?token=D2aZuYtdGL6tUfuV2egoxp";
  const transport = new SSEClientTransport(new URL(url));
  const client = new Client({ name: "test-client", version: "1.0.0" }, {
      capabilities: {}
  });

  try {
      await client.connect(transport);
      console.log("Connected successfully!");
      const toolsResult = await client.listTools();
      const tools = toolsResult.tools.map(t => t.name).join(", ");
      console.log("Available tools:", tools);
      if (tools.includes("navigate") && tools.includes("wait")) {
          console.log("All six tools are accessible.");
      }
      process.exit(0);
  } catch (error) {
      console.error("Connection failed:", error);
      process.exit(1);
  }
}

main();

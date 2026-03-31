import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

export async function POST(req: Request) {
  const { context, question, history } = await req.json();

  if (!process.env.GEMINI_API_KEY) {
    return new Response("GEMINI_API_KEY not configured", { status: 500 });
  }

  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-pro",
    systemInstruction: `You are a senior analyst providing a detailed briefing on a specific topic for a sophisticated Australian investor. The user has seen a summary and wants to go deeper.

Given the context provided, deliver:
1. Detailed analysis (3-5 paragraphs)
2. Key risks and opportunities
3. What to watch next
4. If it's a stock: technical levels, upcoming catalysts, consensus view
5. If it's geopolitical: second-order effects, impact on Australian markets, historical parallels

Be direct, opinionated (with caveats), and specific. No fluff. This person has professional-level knowledge.`,
  });

  const chat = model.startChat({
    history: history || [],
  });

  const result = await chat.sendMessageStream(
    `Context: ${context}\n\nQuestion: ${question}`
  );

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        for await (const chunk of result.stream) {
          const text = chunk.text();
          controller.enqueue(encoder.encode(text));
        }
      } catch (e) {
        controller.enqueue(encoder.encode("\n\n[Error: Stream interrupted]"));
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}

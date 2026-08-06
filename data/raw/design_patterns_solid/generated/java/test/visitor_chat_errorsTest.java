package org.example.patterns;
public class ChatVisitorTest {
    public static void main(String[] args) {
        String out = new ChatLeaf("n").accept(new ChatPrintVisitor());
        if (!out.equals("chat:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

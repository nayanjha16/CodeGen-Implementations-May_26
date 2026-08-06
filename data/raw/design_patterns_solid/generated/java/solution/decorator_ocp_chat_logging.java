// DesignPatternsSolid | kind=combo | label=decorator+ocp | domain=chat | tier=logging
package org.example.patterns;

interface ChatComponent {
    String process(String input);
}

class ChatCore implements ChatComponent {
    public String process(String input) { return "chat:" + input; }
}

public class ChatUpperDecorator implements ChatComponent {
    private final ChatComponent inner;
    public ChatUpperDecorator(ChatComponent inner) { this.inner = inner; }
    public String process(String input) {
        return inner.process(input).toUpperCase();
    }
}

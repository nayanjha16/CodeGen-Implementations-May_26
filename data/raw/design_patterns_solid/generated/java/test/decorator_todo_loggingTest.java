package org.example.patterns;
public class TodoDecoratorTest {
    public static void main(String[] args) {
        TodoComponent c = new TodoUpperDecorator(new TodoCore());
        String out = c.process("ab");
        if (!out.equals("TODO:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

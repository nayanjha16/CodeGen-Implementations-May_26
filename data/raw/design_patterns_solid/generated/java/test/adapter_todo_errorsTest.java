package org.example.patterns;
public class TodoAdapterTest {
    public static void main(String[] args) {
        TodoTarget t = new TodoAdapter(new TodoLegacyApi());
        if (!t.fetch().equals("modern-todo")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}

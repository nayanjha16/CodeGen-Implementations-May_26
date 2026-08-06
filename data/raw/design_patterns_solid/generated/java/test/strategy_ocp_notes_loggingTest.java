package org.example.patterns;
public class NotesStrategyTest {
    public static void main(String[] args) {
        NotesContext ctx = new NotesContext(new NotesDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

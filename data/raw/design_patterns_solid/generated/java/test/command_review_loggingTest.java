package org.example.patterns;
public class ReviewCommandTest {
    public static void main(String[] args) {
        ReviewCommand cmd = new ReviewActionCommand(new ReviewReceiver(), "x");
        if (!cmd.execute().equals("done-review:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

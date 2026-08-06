package org.example.patterns;
public class ReviewDipTest {
    public static void main(String[] args) {
        String out = new ReviewAppService(new ReviewHttpGateway()).publish("p");
        if (!out.equals("http-review:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

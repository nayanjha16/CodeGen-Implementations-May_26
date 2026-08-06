package org.example.patterns;
public class FeedAbstractFactoryTest {
    public static void main(String[] args) {
        String out = FeedAbstractFactoryDemo.run(new FeedCloudFactory());
        if (!out.equals("cloud-btn-feed|cloud-dlg-feed")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

package org.example.patterns;
public class VideoAbstractFactoryTest {
    public static void main(String[] args) {
        String out = VideoAbstractFactoryDemo.run(new VideoCloudFactory());
        if (!out.equals("cloud-btn-video|cloud-dlg-video")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

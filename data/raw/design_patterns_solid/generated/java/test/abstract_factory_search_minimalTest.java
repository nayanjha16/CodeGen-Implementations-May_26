package org.example.patterns;
public class SearchAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SearchAbstractFactoryDemo.run(new SearchCloudFactory());
        if (!out.equals("cloud-btn-search|cloud-dlg-search")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

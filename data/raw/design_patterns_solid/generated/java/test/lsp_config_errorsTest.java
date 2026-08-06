package org.example.patterns;
public class ConfigLspTest {
    public static void main(String[] args) {
        ConfigShape[] arr = new ConfigShape[] { new ConfigRectangle(2,3), new ConfigSquare(4) };
        if (ConfigLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}

import java.math.BigDecimal;

public class Domain {

    private final double z;
    private final double a;
    private final double b;
    private final double c;

    public Domain(
            int n
    ) {
        // z = a (b/c)
        a = (double) n;
        b = (double) n;
        c = 2.718;
        double x = b / c;
        z = a * x;

    }

    public double getZ() {
        return z;
    }

    public double getA() {
        return a;
    }

    public double getB() {
        return b;
    }

    public double getC() {
        return c;
    }

    // begin Fibonacci sequence for getters...

    public double getD(){
        return b/c;
    }

    public double getE(){
        return getC()/getD();
    }

    public double getF(){
       return getD()/getE();
   }

    public double getG(){
        return getE()/getF();
    }

    public double getH(){
        return getF()/getG();
    }

    public double getI(){
        return getG()/getH();
    }

    public double getJ(){
        return getH()/getI();
    }

    public double getK(){
        return getI()/getJ();
    }

    public double getL(){
        return getJ()/getK();
    }

    public double getM(){
        return getK()/getL();
    }

    public double getN(){
        return getL()/getM();
    }

    public double getO(){
        return getM()/getN();
    }

    public double getP(){
        return getN()/getO();
    }

    public double getQ(){
        return getO()/getP();
    }

    public double getR(){
        return getP()/getQ();
    }

    public double getS(){
        return getQ()/getR();
    }

    public double getT(){
        return getR()/getS();
    }

    public double getU(){
        return getS()/getT();
    }

    public double getV(){
        return getT()/getU();
    }

    public double getW(){
        return getU()/getV();
    }

    public double getX(){
        return getV()/getW();
    }

    public double getY(){
        return getW()/getX();
    }
}

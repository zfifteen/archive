public class TestDomain {
    public static void main(String[] args) {
        Domain d = new Domain(1);
        double delta = 1e-10;

        // Test existing getters
        assert Math.abs(d.getD() - d.getB() / d.getC()) < delta : "getD failed";
        assert Math.abs(d.getE() - d.getC() / d.getD()) < delta : "getE failed";
        assert Math.abs(d.getF() - d.getD() / d.getE()) < delta : "getF failed";

        // Test new getters
        assert Math.abs(d.getG() - d.getE() / d.getF()) < delta : "getG failed";
        assert Math.abs(d.getH() - d.getF() / d.getG()) < delta : "getH failed";
        assert Math.abs(d.getI() - d.getG() / d.getH()) < delta : "getI failed";
        assert Math.abs(d.getJ() - d.getH() / d.getI()) < delta : "getJ failed";
        assert Math.abs(d.getK() - d.getI() / d.getJ()) < delta : "getK failed";
        assert Math.abs(d.getL() - d.getJ() / d.getK()) < delta : "getL failed";
        assert Math.abs(d.getM() - d.getK() / d.getL()) < delta : "getM failed";
        assert Math.abs(d.getN() - d.getL() / d.getM()) < delta : "getN failed";
        assert Math.abs(d.getO() - d.getM() / d.getN()) < delta : "getO failed";
        assert Math.abs(d.getP() - d.getN() / d.getO()) < delta : "getP failed";
        assert Math.abs(d.getQ() - d.getO() / d.getP()) < delta : "getQ failed";
        assert Math.abs(d.getR() - d.getP() / d.getQ()) < delta : "getR failed";
        assert Math.abs(d.getS() - d.getQ() / d.getR()) < delta : "getS failed";
        assert Math.abs(d.getT() - d.getR() / d.getS()) < delta : "getT failed";
        assert Math.abs(d.getU() - d.getS() / d.getT()) < delta : "getU failed";
        assert Math.abs(d.getV() - d.getT() / d.getU()) < delta : "getV failed";
        assert Math.abs(d.getW() - d.getU() / d.getV()) < delta : "getW failed";
        assert Math.abs(d.getX() - d.getV() / d.getW()) < delta : "getX failed";
        assert Math.abs(d.getY() - d.getW() / d.getX()) < delta : "getY failed";

        System.out.println("All tests passed!");
    }
}

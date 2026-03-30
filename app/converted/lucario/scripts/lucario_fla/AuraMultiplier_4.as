package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class AuraMultiplier_4 extends MovieClip
    {

        public var cspark:MovieClip;

        public function AuraMultiplier_4()
        {
            super();
            addFrameScript(9, this.frame10, 19, this.frame20, 29, this.frame30, 39, this.frame40, 49, this.frame50, 59, this.frame60, 69, this.frame70, 79, this.frame80, 89, this.frame90);
        }

        internal function frame10():*
        {
            gotoAndStop("min");
        }

        internal function frame20():*
        {
            gotoAndStop("vlow");
        }

        internal function frame30():*
        {
            gotoAndStop("low");
        }

        internal function frame40():*
        {
            gotoAndStop("bmed");
        }

        internal function frame50():*
        {
            gotoAndStop("med");
        }

        internal function frame60():*
        {
            gotoAndStop("amed");
        }

        internal function frame70():*
        {
            gotoAndStop("hi");
        }

        internal function frame80():*
        {
            gotoAndStop("vhi");
        }

        internal function frame90():*
        {
            gotoAndStop("max");
        }


    }
}


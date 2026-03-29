package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class itemGen_mc_18 extends MovieClip
    {

        public var type:String;

        public function itemGen_mc_18()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "itemGen";
            this.visible = false;
        }


    }
}


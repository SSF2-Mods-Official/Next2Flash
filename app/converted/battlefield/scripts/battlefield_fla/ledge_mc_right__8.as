package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class ledge_mc_right__8 extends MovieClip
    {

        public var type:String;

        public function ledge_mc_right__8()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "r_ledge";
            this.visible = false;
        }


    }
}


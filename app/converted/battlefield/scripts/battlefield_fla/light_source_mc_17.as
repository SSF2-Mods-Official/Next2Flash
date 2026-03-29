package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class light_source_mc_17 extends MovieClip
    {

        public var type:String;

        public function light_source_mc_17()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "light_source";
            this.visible = false;
        }


    }
}


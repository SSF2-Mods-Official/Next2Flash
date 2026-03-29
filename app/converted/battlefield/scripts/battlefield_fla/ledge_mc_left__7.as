package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class ledge_mc_left__7 extends MovieClip
    {

        public var type:String;

        public function ledge_mc_left__7()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "l_ledge";
            this.visible = false;
        }


    }
}


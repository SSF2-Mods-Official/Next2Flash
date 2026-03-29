package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p4_Start_12 extends MovieClip
    {

        public var type:String;

        public function p4_Start_12()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p4_start";
            this.visible = false;
        }


    }
}


package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p3_Start_11 extends MovieClip
    {

        public var type:String;

        public function p3_Start_11()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p3_start";
            this.visible = false;
        }


    }
}


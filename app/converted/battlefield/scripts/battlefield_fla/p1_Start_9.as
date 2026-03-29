package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p1_Start_9 extends MovieClip
    {

        public var type:String;

        public function p1_Start_9()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p1_start";
            this.visible = false;
        }


    }
}


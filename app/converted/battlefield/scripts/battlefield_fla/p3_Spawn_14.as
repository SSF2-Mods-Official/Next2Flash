package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p3_Spawn_14 extends MovieClip
    {

        public var type:String;

        public function p3_Spawn_14()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p3_spawn";
            this.visible = false;
        }


    }
}


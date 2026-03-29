package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p2_Spawn_16 extends MovieClip
    {

        public var type:String;

        public function p2_Spawn_16()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p2_spawn";
            this.visible = false;
        }


    }
}


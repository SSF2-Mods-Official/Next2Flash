package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class p1_Spawn_13 extends MovieClip
    {

        public var type:String;

        public function p1_Spawn_13()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "p1_spawn";
            this.visible = false;
        }


    }
}


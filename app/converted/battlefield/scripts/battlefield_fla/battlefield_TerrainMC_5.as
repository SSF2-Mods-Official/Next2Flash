package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class battlefield_TerrainMC_5 extends MovieClip
    {

        public var type:String;

        public function battlefield_TerrainMC_5()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "terrain";
            this.visible = false;
        }


    }
}


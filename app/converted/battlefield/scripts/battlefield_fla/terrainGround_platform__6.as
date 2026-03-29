package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class terrainGround_platform__6 extends MovieClip
    {

        public var type:String;

        public function terrainGround_platform__6()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "platform";
            this.visible = false;
        }


    }
}


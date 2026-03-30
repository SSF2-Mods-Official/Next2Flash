package
{
    import flash.display.MovieClip;

    public dynamic class zelda_select extends MovieClip
    {

        public var characterID:String;

        public function zelda_select()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.characterID = "zelda";
        }


    }
}


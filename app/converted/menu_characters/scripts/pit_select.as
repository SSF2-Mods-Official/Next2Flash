package
{
    import flash.display.MovieClip;

    public dynamic class pit_select extends MovieClip
    {

        public var characterID:String;

        public function pit_select()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.characterID = "pit";
        }


    }
}


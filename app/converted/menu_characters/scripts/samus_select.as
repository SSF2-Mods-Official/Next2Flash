package
{
    import flash.display.MovieClip;

    public dynamic class samus_select extends MovieClip
    {

        public var characterID:String;

        public function samus_select()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.characterID = "samus";
        }


    }
}


package
{
    import flash.display.MovieClip;
    import flash.display.SimpleButton;
    import flash.text.TextField;

    public dynamic class CharacterSelectBox extends MovieClip
    {

        public var charPortrait:MovieClip;
        public var controlType:MovieClip;
        public var flag:MovieClip;
        public var icon:blankmc2;
        public var levelDisplay:MovieClip;
        public var nameDisplay:MovieClip;
        public var nextExp:SimpleButton;
        public var pic:blankmc2;
        public var playerTitle:MovieClip;
        public var playerTxt:TextField;

        public function CharacterSelectBox()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2);
        }

        internal function frame1():*
        {
            stop();
        }

        internal function frame2():*
        {
            stop();
        }


    }
}


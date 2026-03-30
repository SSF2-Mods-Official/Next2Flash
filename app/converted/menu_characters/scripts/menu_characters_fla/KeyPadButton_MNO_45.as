package menu_characters_fla
{
    import flash.display.MovieClip;
    import flash.text.TextField;

    public dynamic class KeyPadButton_MNO_45 extends MovieClip
    {

        public var btn_txt:TextField;

        public function KeyPadButton_MNO_45()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.buttonMode = true;
            this.mouseChildren = false;
        }


    }
}


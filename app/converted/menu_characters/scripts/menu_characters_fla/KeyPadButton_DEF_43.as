package menu_characters_fla
{
    import flash.display.MovieClip;
    import flash.text.TextField;

    public dynamic class KeyPadButton_DEF_43 extends MovieClip
    {

        public var btn_txt:TextField;

        public function KeyPadButton_DEF_43()
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


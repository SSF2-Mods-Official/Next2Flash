package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_15 extends MovieClip
    {

        public function Win_15()
        {
            super();
            addFrameScript(30, this.frame31, 46, this.frame47, 87, this.frame88, 88, this.frame89, 112, this.frame113, 130, this.frame131, 155, this.frame156, 156, this.frame157, 165, this.frame166, 178, this.frame179, 190, this.frame191, 204, this.frame205, 218, this.frame219, 229, this.frame230, 231, this.frame232);
        }

        internal function frame31():*
        {
            if (SSF2API.isReady())
            {
                gotoAndPlay(("win" + SSF2API.randomInteger(1, 3).toString()));
            };
        }

        internal function frame47():*
        {
        }

        internal function frame88():*
        {
            this.gotoAndStop("loop1");
        }

        internal function frame89():*
        {
            SSF2API.playSound("ring");
        }

        internal function frame113():*
        {
            SSF2API.playSound("ring");
            SSF2API.playSound("beep_3");
        }

        internal function frame131():*
        {
            SSF2API.playSound("ring");
            SSF2API.playSound("beep_3");
        }

        internal function frame156():*
        {
            this.gotoAndStop("loop2");
        }

        internal function frame157():*
        {
            SSF2API.playSound("beep_3");
        }

        internal function frame166():*
        {
            SSF2API.playSound("beep_2");
        }

        internal function frame179():*
        {
            SSF2API.playSound("beep_3");
        }

        internal function frame191():*
        {
            SSF2API.playSound("beep_4");
        }

        internal function frame205():*
        {
            SSF2API.playSound("beep_3");
        }

        internal function frame219():*
        {
            SSF2API.playSound("beep_2");
        }

        internal function frame230():*
        {
            SSF2API.playSound("beep5");
        }

        internal function frame232():*
        {
            this.gotoAndStop("loop3");
        }


    }
}


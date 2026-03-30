package
{
    import flash.display.MovieClip;

    public dynamic class effect_bdee_land extends MovieClip
    {

        public var rand:*;

        public function effect_bdee_land()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 20, this.frame21, 30, this.frame31);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.rand = SSF2API.randomInteger(1, 3);
                if (this.rand == 1)
                {
                    gotoAndStop(2);
                }
                else if (this.rand == 2)
                {
                    gotoAndStop(12);
                }
                else if (this.rand == 3)
                {
                    gotoAndStop(22);
                };
            };
        }

        internal function frame11():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }

        internal function frame21():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }

        internal function frame31():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}


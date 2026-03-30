package
{
    import flash.display.MovieClip;

    public dynamic class effect_lucario_spheretrail extends MovieClip
    {

        public var rand:*;

        public function effect_lucario_spheretrail()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12, 22, this.frame23, 33, this.frame34, 44, this.frame45);
        }

        internal function frame1():*
        {
            this.rand = SSF2API.safeRandom();
            if (this.rand < 0.25)
            {
                gotoAndStop("trail1");
            }
            else if (this.rand < 0.5)
            {
                gotoAndStop("trail2");
            }
            else if (this.rand < 0.75)
            {
                gotoAndStop("trail3");
            }
            else
            {
                gotoAndStop("trail4");
            };
        }

        internal function frame12():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }

        internal function frame23():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }

        internal function frame34():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }

        internal function frame45():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}


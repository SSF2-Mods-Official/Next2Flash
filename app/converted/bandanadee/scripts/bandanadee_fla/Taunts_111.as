package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunts_111 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Taunts_111()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 27, this.frame28, 30, this.frame31, 33, this.frame34, 42, this.frame43, 52, this.frame53, 62, this.frame63, 73, this.frame74, 76, this.frame77, 79, this.frame80, 113, this.frame114, 114, this.frame115);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", true);
            };
        }

        internal function frame3():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("bandanadee_taunt");
            };
        }

        internal function frame28():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_step01");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }

        internal function frame34():*
        {
            this.self.playSound("bandanadee_jump1");
        }

        internal function frame43():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }

        internal function frame53():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }

        internal function frame63():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }

        internal function frame74():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
            };
        }

        internal function frame77():*
        {
            this.self.endAttack();
        }

        internal function frame80():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_fspecEnd");
            };
        }

        internal function frame114():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-20});
        }

        internal function frame115():*
        {
            this.self.endAttack();
        }


    }
}


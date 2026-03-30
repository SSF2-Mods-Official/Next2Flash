package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunt_86 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function Taunt_86()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 12, this.frame13, 22, this.frame23, 32, this.frame33, 33, this.frame34, 39, this.frame40, 42, this.frame43, 49, this.frame50, 63, this.frame64, 82, this.frame83, 86, this.frame87, 90, this.frame91, 94, this.frame95, 123, this.frame124);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame5():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("chibi_OpenHead");
            };
        }

        internal function frame7():*
        {
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(2),
                "y":-40,
                "parentLock":true
            });
        }

        internal function frame13():*
        {
            if (this.self.isFacingRight())
            {
                this.self.stancePlayFrame("neutralright");
            }
            else
            {
                this.self.stancePlayFrame("neutralleft");
            };
        }

        internal function frame23():*
        {
            this.self.stancePlayFrame("continueneutral");
        }

        internal function frame33():*
        {
            this.self.stancePlayFrame("continueneutral");
        }

        internal function frame34():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("chibi_CloseHead");
            };
        }

        internal function frame40():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(2),
                "y":-38
            });
        }

        internal function frame43():*
        {
            SSF2API.getCharacter(this).endAttack();
        }

        internal function frame50():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("chibi_OpenHead", true);
            };
            this.self.attachEffect("chibirobo_effect_lidopen", {
                "x":this.self.flipX(-1.6),
                "y":-42
            });
        }

        internal function frame64():*
        {
            this.self.playSound("chibi_Bend");
        }

        internal function frame83():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("chibi_CloseHead");
            };
        }

        internal function frame87():*
        {
            this.self.attachEffect("chibirobo_effect_lidclose", {
                "x":this.self.flipX(2.2),
                "y":-38
            });
        }

        internal function frame91():*
        {
            this.self.endAttack();
        }

        internal function frame95():*
        {
            this.self.attachEffectOverlay("soapBubbles", {
                "x":this.self.flipX(-25),
                "y":1
            });
            this.self.attachEffectOverlay("floorTwinkle", {
                "x":this.self.flipX(-25),
                "y":1
            });
        }

        internal function frame124():*
        {
            this.self.endAttack();
        }


    }
}


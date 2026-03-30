package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_jumpair_20 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var done:*;

        public function bomberman_jumpair_20()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.done = false;
            if (this.self && SSF2API.isReady())
            {
                if (this.self.getGlobalVariable("screwAttackOn") && (this.self.getMidairJumpCount() < 2))
                {
                    this.self.forceAttack("item_screw");
                }
                else if (this.self.getGlobalVariable("sonicShieldFiredash") && (this.self.getControls().LEFT || this.self.getControls().RIGHT))
                {
                    this.self.forceAttack("item_firedash");
                }
                else if (this.self.getGlobalVariable("sonicShieldBubbleBounce") && this.self.getControls().DOWN)
                {
                    this.self.forceAttack("item_bubblebounce");
                }
                else
                {
                    this.self.playSound("bomberman_jump2");
                };
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bomberman_jumpflip");
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}


package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class NAirOLD_53 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:*;

        public function NAirOLD_53()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 9, this.frame10, 18, this.frame19, 21, this.frame22, 23, this.frame24, 31, this.frame32);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getCharacter(this);
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame4():*
        {
            this.self.playSound("gw_usmash");
            this.self.playSound("whoosh1");
            this.self.setLandingLag(true);
            this.self.updateAttackBoxStats(1, {
                "damage":12,
                "direction":40,
                "power":60,
                "kbConstant":98,
                "effectSound":"brawl_kick_l",
                "hitStun":4,
                "selfHitStun":3,
                "reversableAngle":false
            });
            this.self.updateAttackBoxStats(2, {
                "damage":12,
                "direction":40,
                "power":60,
                "kbConstant":98,
                "effectSound":"brawl_kick_l",
                "hitStun":4,
                "selfHitStun":3,
                "reversableAngle":false
            });
        }

        internal function frame9():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame10():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":7,
                "hitStun":3,
                "selfHitStun":2
            });
            this.self.updateAttackBoxStats(2, {
                "damage":7,
                "hitStun":3,
                "selfHitStun":2
            });
        }

        internal function frame19():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame22():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}


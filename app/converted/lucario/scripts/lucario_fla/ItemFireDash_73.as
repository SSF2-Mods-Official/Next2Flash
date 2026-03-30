package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFireDash_73 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var updateStats:*;

        public function ItemFireDash_73()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 10, this.frame11, 16, this.frame17, 17, this.frame18, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.updateStats = true;
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                this.self.setLandingLag(true);
                this.self.playSound("sonic_shieldfire_dash");
            };
        }

        internal function frame7():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "allowControl":true,
                "allowFastFall":false
            });
        }

        internal function frame9():*
        {
            this.self.updateAttackStats({"allowFastFall":true});
        }

        internal function frame11():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }

        internal function frame18():*
        {
            this.self.updateAuraPaws();
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("lucario_land02");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}


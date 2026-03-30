package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFireDash_96 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function ItemFireDash_96()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 10, this.frame11, 16, this.frame17, 17, this.frame18, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady() && this.self)
            {
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
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}


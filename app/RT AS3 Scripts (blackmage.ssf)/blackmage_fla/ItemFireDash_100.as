// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemFireDash_100

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemFireDash_100 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemFireDash_100()
        {
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 10, this.frame11, 16, this.frame17, 17, this.frame18, 24, this.frame25);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((SSF2API.isReady()) && (this.self)))
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
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

